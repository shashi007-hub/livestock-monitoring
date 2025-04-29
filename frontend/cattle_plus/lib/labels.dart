class Labels {
  static const Map<String, Map<String, String>> text = {
    'en': {
      'actionCenter': 'Action Center',
      'settings': 'Settings',
      'search': 'Search',
      'weatherToday': 'Weather Today',
      'myAnimals': 'My Animals',
      'callVet': 'Call Vet',
      'problemIdentified': 'Problem Identified',
      'possibleSolution': 'Possible Solution',
    },
    'hi': {
      'actionCenter': 'कार्य केंद्र',
      'settings': 'सेटिंग्स',
      'search': 'खोज',
      'weatherToday': 'आज का मौसम',
      'myAnimals': 'मेरे पशु',
      'callVet': 'पशु चिकित्सक को बुलाएं',
      'problemIdentified': 'पहचानी गई समस्या',
      'possibleSolution': 'संभावित समाधान',
    }
  };

  static String translate(String key, String languageCode) {
    return text[languageCode]?[key] ?? key;
  }
}
