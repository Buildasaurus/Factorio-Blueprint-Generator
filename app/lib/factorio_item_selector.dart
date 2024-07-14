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
    const int columnCount = 9;
    const int rowCount = 8;

    final InventoryLayoutGroup imageNames = loadJson()[inventoryIndex];

    return GridView.builder(
      gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
        crossAxisCount: columnCount, // Adjust the number of columns as needed
        crossAxisSpacing: 8.0,
        mainAxisSpacing: 8.0,
      ),
      itemCount: columnCount * rowCount,
      itemBuilder: (context, index) {
        String? iconPath = imageNames.subgroups.length > index ~/ columnCount &&
                imageNames.subgroups[index ~/ columnCount].items.length > index % columnCount
            ? imageNames.subgroups[index ~/ columnCount].items[index % columnCount].icon
            : null;
        if (iconPath != null) {
          return IconButton(
            style: ButtonStyle(
              padding: WidgetStateProperty.all(EdgeInsets.zero),
                shape: WidgetStateProperty.all<RoundedRectangleBorder>(
                    const RoundedRectangleBorder(
                        borderRadius: BorderRadius.zero,
                        side: BorderSide(color: Colors.red)))),
            icon: Stack(
              children: [
                const Image(
                  image: AssetImage("assets/slot.png"),
                  height: 100,
                  width: 100,
                ),
                Image(
                  image: Resources.instance.getImage(iconPath),
                  height: 100,
                  width: 100,
                ),
              ],
            ),
            onPressed: () => debugPrint(iconPath),
            hoverColor: Colors.black,
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
