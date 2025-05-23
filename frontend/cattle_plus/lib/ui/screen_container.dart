import 'package:cattle_plus/ui/screens/home/home_ui.dart';
import 'package:cattle_plus/ui/screens/my_animals/myanimals.dart';
import 'package:cattle_plus/ui/screens/search/search_ui.dart';
import 'package:cattle_plus/ui/screens/settings/settings.dart';
import 'package:flutter/material.dart';
import 'package:persistent_bottom_nav_bar_v2/persistent_bottom_nav_bar_v2.dart';
import 'package:easy_localization/easy_localization.dart';

class ScreenContainer extends StatelessWidget {
  const ScreenContainer({super.key});

  @override
  Widget build(BuildContext context) {
    return PersistentTabView(
      tabs: [
        PersistentTabConfig(
          screen: HomeScreen(),
          item: ItemConfig(icon: Icon(Icons.home), title: "Home".tr()),
        ),
        PersistentTabConfig(
          screen: SearchUI(),
          item: ItemConfig(icon: Icon(Icons.message), title: "Messages".tr()),
        ),
        PersistentTabConfig(
          screen: SettingsUI(),
          item: ItemConfig(icon: Icon(Icons.settings), title: "Settings".tr()),
        ),
      ],
      navBarBuilder:
          (navBarConfig) => Style8BottomNavBar(navBarConfig: navBarConfig),
      resizeToAvoidBottomInset: true,
    );
  }
}
