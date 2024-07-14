import 'dart:convert';
import 'dart:io';

import 'package:factorio_blueprint_generator/Resources.dart';
import 'package:factorio_blueprint_generator/inventory_model.dart';
import 'package:flutter/material.dart';

class FactorioItemSelector extends StatelessWidget {
  final int inventoryIndex;
  const FactorioItemSelector({super.key, required this.inventoryIndex});

  @override
  Widget build(BuildContext context) {
    final InventoryLayoutGroup imageNames = loadJson()[inventoryIndex];

    return GridView.builder(
      gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
        crossAxisCount: 9, // Adjust the number of columns as needed
        crossAxisSpacing: 8.0,
        mainAxisSpacing: 8.0,
      ),
      itemCount: 9 * 8,
      itemBuilder: (context, index) {
        String name = imageNames.subgroups.length > index ~/ 9 &&
                imageNames.subgroups[index ~/ 9].items.length > index % 9
            ? imageNames.subgroups[index ~/ 9].items[index % 9].name
            : "";
        if (name != "") {
          return Stack(
            children: [
              const Image(
                image: AssetImage("assets/slot.png"),
                height: 100,
                width: 100,
              ),
              Image(
                image: Resources.instance.getImage(name),
                height: 100,
                width: 100,
              ),
            ],
          );
        }
        return Container();
      },
    );
  }

  List<InventoryLayoutGroup> loadJson() {
    String jsonString = File("InventoryStrucutre.json").readAsStringSync();
    // Deserialize JSON to Dart object
    List<dynamic> jsonMap = jsonDecode(jsonString);
    List<InventoryLayoutGroup> list = [];
    for (dynamic a in jsonMap) {
      list.add(InventoryLayoutGroup.fromJson(a));
    }
    return list;
  }
}
