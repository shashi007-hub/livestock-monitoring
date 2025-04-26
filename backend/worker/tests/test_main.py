import pytest
import json
import queue
from unittest.mock import Mock, patch, MagicMock
import time
from collections import defaultdict

# Import the functions we want to test
from app.main import (
    on_message,
    run_inference_and_publish,
    mqtt_subscribe,
    MQTT_TOPIC_MIC,
    MQTT_TOPIC_ACC,
    MQTT_TOPIC_CAMERA,
    BATCH_THRESHOLD,
    topic_queues,
    WORKER_ID
)

@pytest.fixture
def mock_mqtt_client():
    return Mock()

@pytest.fixture
def reset_topic_queues():
    # Reset topic queues before each test
    for topic in topic_queues:
        topic_queues[topic] = defaultdict(queue.Queue)
    yield
    # Cleanup after test
    for topic in topic_queues:
        topic_queues[topic] = defaultdict(queue.Queue)

def create_test_message(topic, bovine_id, value=0.5):
    """Helper to create test messages"""
    if topic == MQTT_TOPIC_MIC:
        return {"bovine_id": bovine_id, "probability": value}
    elif topic == MQTT_TOPIC_ACC:
        return {"bovine_id": bovine_id, "metric": value}
    else:  # Camera
        return {"bovine_id": bovine_id, "probability": value}

class TestMessageHandling:
    
    @pytest.mark.parametrize("topic,bovine_id,value", [
        (MQTT_TOPIC_MIC, 1, 0.7),
        (MQTT_TOPIC_ACC, 2, 0.6),
        (MQTT_TOPIC_CAMERA, 3, 0.8),
    ])
    def test_on_message_valid_json(self, mock_mqtt_client, reset_topic_queues, topic, bovine_id, value):
        """Test handling of valid messages for different topics"""
        message = create_test_message(topic, bovine_id, value)
        msg = Mock()
        msg.topic = topic
        msg.payload = json.dumps(message).encode()
        
        on_message(mock_mqtt_client, None, msg)
        
        assert not topic_queues[topic][bovine_id].empty()
        queued_msg = topic_queues[topic][bovine_id].get()
        assert queued_msg["bovine_id"] == bovine_id
        assert queued_msg["topic"] == topic

    def test_on_message_invalid_json(self, mock_mqtt_client, reset_topic_queues):
        """Test handling of invalid JSON message"""
        msg = Mock()
        msg.topic = MQTT_TOPIC_MIC
        msg.payload = b"invalid json"
        
        on_message(mock_mqtt_client, None, msg)
        
        assert topic_queues[MQTT_TOPIC_MIC][1].empty()

    def test_on_message_missing_bovine_id(self, mock_mqtt_client, reset_topic_queues):
        """Test handling of message without bovine_id"""
        msg = Mock()
        msg.topic = MQTT_TOPIC_MIC
        msg.payload = json.dumps({"probability": 0.5}).encode()
        
        on_message(mock_mqtt_client, None, msg)
        
        # Should not queue message without bovine_id
        for bovine_queue in topic_queues[MQTT_TOPIC_MIC].values():
            assert bovine_queue.empty()

class TestBatchProcessing:

    @pytest.mark.parametrize("topic", [MQTT_TOPIC_MIC, MQTT_TOPIC_ACC, MQTT_TOPIC_CAMERA])
    def test_batch_processing_threshold(self, reset_topic_queues, topic):
        """Test batch processing when threshold is reached"""
        bovine_id = 1
        q = topic_queues[topic][bovine_id]
        
        # Add BATCH_THRESHOLD messages
        for i in range(BATCH_THRESHOLD):
            message = create_test_message(topic, bovine_id, 0.5 + i/10)
            message["topic"] = topic
            q.put(message)
            
        with patch('app.mapping.topic_to_pipeline') as mock_pipeline_dict:
            mock_pipeline = Mock(return_value={"status": "success"})
            mock_pipeline_dict.__getitem__.return_value = mock_pipeline
            result = run_inference_and_publish(q)
            
        assert result is not None
        assert result["status"] == "success"
        assert q.empty()  # Queue should be empty after processing

    def test_batch_processing_mixed_bovines(self, reset_topic_queues):
        """Test that messages from different bovines don't get mixed in batch"""
        topic = MQTT_TOPIC_MIC
        q = topic_queues[topic][1]  # Queue for bovine 1
        
        # Add messages for bovine 1
        for i in range(3):
            message = create_test_message(topic, 1, 0.5)
            message["topic"] = topic
            q.put(message)
            
        # Add message for bovine 2
        message = create_test_message(topic, 2, 0.6)
        message["topic"] = topic
        q.put(message)
        
        with patch('app.mapping.topic_to_pipeline') as mock_pipeline_dict:
            mock_pipeline = Mock(return_value={"status": "success"})
            mock_pipeline_dict.__getitem__.return_value = mock_pipeline
            result = run_inference_and_publish(q)
            
        assert result is None  # Should not process incomplete batch
        assert q.qsize() == 4  # All messages should still be in queue

class TestMQTTClient:

    def test_mqtt_subscribe(self, monkeypatch):
        """Test MQTT client subscription"""
        mock_client = MagicMock()
        monkeypatch.setattr('paho.mqtt.client.Client', lambda: mock_client)
        
        client = mqtt_subscribe()
        
        assert mock_client.connect.called
        assert mock_client.subscribe.called
        assert mock_client.loop_start.called
        
        # Verify subscribed to all topics
        topics = [MQTT_TOPIC_MIC, MQTT_TOPIC_ACC, MQTT_TOPIC_CAMERA]
        subscribe_args = mock_client.subscribe.call_args[0][0]
        assert all(topic in str(subscribe_args) for topic in topics)

@pytest.mark.integration
class TestIntegration:

    def test_end_to_end_flow(self, reset_topic_queues):
        """Test complete flow from message reception to batch processing"""
        topic = MQTT_TOPIC_MIC
        bovine_id = 1
        
        # Simulate receiving BATCH_THRESHOLD messages
        for i in range(BATCH_THRESHOLD):
            msg = Mock()
            msg.topic = topic
            message = create_test_message(topic, bovine_id, 0.5 + i/10)
            msg.payload = json.dumps(message).encode()
            on_message(None, None, msg)
            
        q = topic_queues[topic][bovine_id]
        assert q.qsize() == BATCH_THRESHOLD
        
        with patch('app.mapping.topic_to_pipeline') as mock_pipeline_dict:
            mock_pipeline = Mock(return_value={"status": "success"})
            mock_pipeline_dict.__getitem__.return_value = mock_pipeline
            result = run_inference_and_publish(q)
            
        assert result is not None
        assert result["status"] == "success"
        assert q.empty()

if __name__ == '__main__':
    pytest.main(['-v', __file__])