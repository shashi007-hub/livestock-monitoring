import 'dart:convert';
import 'dart:io';
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:image_picker/image_picker.dart';
import 'package:fluttertoast/fluttertoast.dart';
import 'add_animal_cubit.dart';
import 'add_animal_states.dart';

class AddAnimalScreen extends StatefulWidget {
  const AddAnimalScreen({super.key});

  @override
  State<AddAnimalScreen> createState() => _AddAnimalScreenState();
}

class _AddAnimalScreenState extends State<AddAnimalScreen> {
  final _formKey = GlobalKey<FormState>();
  final _nameController = TextEditingController();
  final _ageController = TextEditingController();
  final _weightController = TextEditingController();
  final _fatherIdController = TextEditingController();
  final _motherIdController = TextEditingController();
  BreedType _selectedBreed = BreedType.GIR;
  File? _imageFile;
  bool _isPickingImage = false;

  @override
  Widget build(BuildContext context) {
    return BlocProvider(
      create: (context) => AddAnimalCubit(),
      child: BlocConsumer<AddAnimalCubit, AddAnimalState>(
        listener: (context, state) {
          if (state is AddAnimalSuccess) {
            Fluttertoast.showToast(msg: 'Animal added successfully!');
            Navigator.pop(context, true);
          } else if (state is AddAnimalError) {
            Fluttertoast.showToast(msg: state.message);
          }
        },
        builder: (context, state) {
          return Scaffold(
            appBar: AppBar(title: const Text('Add New Animal')),
            body: SafeArea(
              child: Scrollbar(
                thumbVisibility: true,
                child: SingleChildScrollView(
                  padding: const EdgeInsets.fromLTRB(16, 16, 16, 32),
                  child: Form(
                    key: _formKey,
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.stretch,
                      children: [
                        GestureDetector(
                          onTap: _pickImage,
                          child: Container(
                            height: 200,
                            decoration: BoxDecoration(
                              color: Colors.grey[200],
                              borderRadius: BorderRadius.circular(12),
                            ),
                            child:
                                _imageFile != null
                                    ? ClipRRect(
                                      borderRadius: BorderRadius.circular(12),
                                      child: Image.file(
                                        _imageFile!,
                                        fit: BoxFit.cover,
                                      ),
                                    )
                                    : const Icon(Icons.add_a_photo, size: 50),
                          ),
                        ),
                        const SizedBox(height: 16),
                        TextFormField(
                          controller: _nameController,
                          decoration: const InputDecoration(
                            labelText: 'Name',
                            border: OutlineInputBorder(),
                          ),
                          validator:
                              (value) =>
                                  value?.isEmpty ?? true
                                      ? 'Name is required'
                                      : null,
                        ),
                        const SizedBox(height: 16),
                        TextFormField(
                          controller: _ageController,
                          decoration: const InputDecoration(
                            labelText: 'Age',
                            border: OutlineInputBorder(),
                          ),
                          keyboardType: TextInputType.number,
                          validator:
                              (value) =>
                                  value?.isEmpty ?? true
                                      ? 'Age is required'
                                      : null,
                        ),
                        const SizedBox(height: 16),
                        TextFormField(
                          controller: _weightController,
                          decoration: const InputDecoration(
                            labelText: 'Weight',
                            border: OutlineInputBorder(),
                          ),
                          keyboardType: TextInputType.number,
                          validator:
                              (value) =>
                                  value?.isEmpty ?? true
                                      ? 'Weight is required'
                                      : null,
                        ),
                        const SizedBox(height: 16),
                        DropdownButtonFormField<BreedType>(
                          value: _selectedBreed,
                          decoration: const InputDecoration(
                            labelText: 'Breed',
                            border: OutlineInputBorder(),
                          ),
                          items:
                              BreedType.values.map((breed) {
                                return DropdownMenuItem(
                                  value: breed,
                                  child: Text(breed.displayName),
                                );
                              }).toList(),
                          onChanged: (value) {
                            setState(() {
                              _selectedBreed = value!;
                            });
                          },
                        ),
                        const SizedBox(height: 16),
                        TextFormField(
                          controller: _fatherIdController,
                          decoration: const InputDecoration(
                            labelText: 'Father ID (Optional)',
                            border: OutlineInputBorder(),
                          ),
                        ),
                        const SizedBox(height: 16),
                        TextFormField(
                          controller: _motherIdController,
                          decoration: const InputDecoration(
                            labelText: 'Mother ID (Optional)',
                            border: OutlineInputBorder(),
                          ),
                        ),
                        const SizedBox(height: 24),
                        ElevatedButton(
                          onPressed:
                              state is AddAnimalLoading
                                  ? null
                                  : () => _submitForm(context),
                          style: ElevatedButton.styleFrom(
                            padding: const EdgeInsets.symmetric(vertical: 16),
                          ),
                          child:
                              state is AddAnimalLoading
                                  ? const CircularProgressIndicator()
                                  : const Text('Add Animal'),
                        ),
                      ],
                    ),
                  ),
                ),
              ),
            ),
          );
        },
      ),
    );
  }

  Future<void> _pickImage() async {
    if (_isPickingImage) return; // Prevent concurrent picking operations

    try {
      setState(() {
        _isPickingImage = true;
      });

      final picker = ImagePicker();
      final pickedFile = await picker.pickImage(source: ImageSource.gallery);
      if (pickedFile != null) {
        setState(() {
          _imageFile = File(pickedFile.path);
        });
      }
    } finally {
      setState(() {
        _isPickingImage = false;
      });
    }
  }

  void _submitForm(BuildContext context) async {
    if (!_formKey.currentState!.validate()) return;
    if (_imageFile == null) {
      Fluttertoast.showToast(msg: 'Please select an image');
      return;
    }

    final bytes = await _imageFile!.readAsBytes();
    final base64Image = base64Encode(bytes);

    context.read<AddAnimalCubit>().addBovine(
      name: _nameController.text,
      age: int.parse(_ageController.text),
      weight: double.parse(_weightController.text),
      breed: _selectedBreed.displayName,
      fatherId:
          _fatherIdController.text.isEmpty ? null : _fatherIdController.text,
      motherId:
          _motherIdController.text.isEmpty ? null : _motherIdController.text,
      imageBase64: base64Image,
    );
  }

  @override
  void dispose() {
    _nameController.dispose();
    _ageController.dispose();
    _weightController.dispose();
    _fatherIdController.dispose();
    _motherIdController.dispose();
    super.dispose();
  }
}
