import 'dart:math';
import 'dart:ui';

import 'package:cattle_plus/const.dart';
import 'package:cattle_plus/routing/routes.dart';
import 'package:cattle_plus/ui/components/animal_tile.dart';
import 'package:cattle_plus/ui/components/weather_widget.dart';
import 'package:cattle_plus/ui/screens/add_animal/add_animal.dart';
import 'package:cattle_plus/ui/screens/home/home_cubit.dart';
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:easy_localization/easy_localization.dart';

class HomeScreen extends StatelessWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return SafeArea(
      child: BlocProvider(
        create: (context) => HomeCubit()..loadHomeData(),
        child: BlocBuilder<HomeCubit, HomeState>(
          builder: (context, state) {
            if (state is HomeLoading) {
              return const Center(child: CircularProgressIndicator());
            }

            final random = Random();
            return Scaffold(
              floatingActionButton: FloatingActionButton(
                onPressed: () async {
                  final result = await Navigator.push(
                    context,
                    MaterialPageRoute(builder: (context) => AddAnimalScreen()),
                  );
                  // If result is true, refresh the home data
                  if (result == true) {
                    context.read<HomeCubit>().loadHomeData();
                  }
                },
                child: const Icon(Icons.add),
              ),
              body: CustomScrollView(
                slivers: [
                  SliverAppBar(
                    expandedHeight: 100,
                    flexibleSpace: LayoutBuilder(
                      builder: (context, constraints) {
                        var top = constraints.biggest.height;
                        bool isCollapsed =
                            top <=
                            kToolbarHeight + MediaQuery.of(context).padding.top;

                        return FlexibleSpaceBar(
                          title: isCollapsed ? Text('Home'.tr()) : null,
                          centerTitle: true,
                          background: Center(
                            child: Row(
                              mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                              crossAxisAlignment: CrossAxisAlignment.center,
                              children: [
                                Container(
                                  height: 70,
                                  decoration: BoxDecoration(
                                    color: const Color.fromARGB(
                                      255,
                                      214,
                                      221,
                                      215,
                                    ).withOpacity(0.2),
                                    borderRadius: BorderRadius.circular(20),
                                    border: Border.all(
                                      color: Colors.white.withOpacity(0.3),
                                    ),
                                  ),
                                  child: BackdropFilter(
                                    filter: ImageFilter.blur(
                                      sigmaX: 10,
                                      sigmaY: 10,
                                    ),
                                    child: Column(
                                      mainAxisAlignment:
                                          MainAxisAlignment.center,
                                      children: [
                                        Text(
                                          'Anomalies'.tr(),
                                          style: TextStyle(color: Colors.black),
                                        ),
                                        Row(
                                          children: [
                                            const Icon(
                                              Icons.warning_amber_outlined,
                                              color: Color.fromARGB(
                                                255,
                                                231,
                                                11,
                                                3,
                                              ),
                                            ),
                                            const SizedBox(width: 5),
                                            Text(
                                              '${state.anomalies}',
                                              style: const TextStyle(
                                                fontSize: 30,
                                                color: Colors.black,
                                              ),
                                            ),
                                          ],
                                        ),
                                      ],
                                    ),
                                  ),
                                ),
                                Column(
                                  mainAxisAlignment: MainAxisAlignment.center,
                                  children: [
                                    Text(
                                      'Avg Steps'.tr(),
                                      style: TextStyle(color: Colors.black),
                                    ),
                                    Row(
                                      children: [
                                        const Icon(
                                          Icons.directions_walk_outlined,
                                          color: Colors.green,
                                        ),
                                        const SizedBox(width: 5),
                                        Text(
                                          '${state.averageSteps}',
                                          style: const TextStyle(
                                            fontSize: 30,
                                            color: Colors.black,
                                          ),
                                        ),
                                      ],
                                    ),
                                  ],
                                ),
                                Column(
                                  mainAxisAlignment: MainAxisAlignment.center,
                                  children: [
                                    Text(
                                      'Grazing Volume'.tr(),
                                      style: TextStyle(color: Colors.black),
                                    ),
                                    Row(
                                      children: [
                                        const Icon(
                                          Icons.water_drop_outlined,
                                          color: Colors.blue,
                                        ),
                                        const SizedBox(width: 5),
                                        Text(
                                          '${state.grazingVolume}',
                                          style: const TextStyle(
                                            fontSize: 30,
                                            color: Colors.black,
                                          ),
                                        ),
                                      ],
                                    ),
                                  ],
                                ),
                              ],
                            ),
                          ),
                        );
                      },
                    ),
                    pinned: true,
                  ),
                  // --- SORTED ANIMAL TILES ---
                  Builder(
                    builder: (context) {
                      // Pair each bovine with its status
                      final bovineStatusList =
                          state.bovines.map((bovine) {
                            final status = state.statuses.firstWhere(
                              (s) => s.bovineId == bovine.id,
                              orElse:
                                  () => BovineStatus(
                                    bovineId: bovine.id,
                                    status: 'normal',
                                  ),
                            );
                            return {'bovine': bovine, 'status': status};
                          }).toList();

                      // Sort by danger > needs attention > normal
                      bovineStatusList.sort((a, b) {
                        int getRank(String status) {
                          switch (_mapStatusToEnum(status)) {
                            case AnimalStatus.danger:
                              return 0;
                            case AnimalStatus.needsAttention:
                              return 1;
                            case AnimalStatus.normal:
                            default:
                              return 2;
                          }
                        }

                        final aStatus = (a['status'] as BovineStatus).status;
                        final bStatus = (b['status'] as BovineStatus).status;
                        return getRank(aStatus).compareTo(getRank(bStatus));
                      });

                      return SliverList(
                        delegate: SliverChildBuilderDelegate((context, index) {
                          if (index == 0) {
                            return WeatherWidget(
                              username: state.username,
                              city: state.city,
                            );
                          }

                          final bovineIndex = index - 1;
                          if (bovineIndex >= bovineStatusList.length) {
                            return null;
                          }

                          final bovine =
                              bovineStatusList[bovineIndex]['bovine'] as Bovine;
                          final status =
                              bovineStatusList[bovineIndex]['status']
                                  as BovineStatus;

                          return AnimalTile(
                            onTap:
                                () => Navigator.pushNamed(
                                  context,
                                  Routes.ANIMAL_SUMMARY,
                                  arguments: bovine.id.toString(),
                                ),
                            name: bovine.name,
                            status: _mapStatusToEnum(status.status),
                            lastSeen:
                                DateTime.now(), // This should come from the API
                            imageUrl: context
                                .read<HomeCubit>()
                                .getBovineImageUrl(bovine.id),
                          );
                        }),
                      );
                    },
                  ),
                ],
              ),
            );
          },
        ),
      ),
    );
  }

  AnimalStatus _mapStatusToEnum(String status) {
    switch (status.toLowerCase()) {
      case 'normal':
        return AnimalStatus.normal;
      case 'danger':
        return AnimalStatus.danger;
      case 'needsattention':
        return AnimalStatus.needsAttention;
      default:
        return AnimalStatus.normal;
    }
  }
}
