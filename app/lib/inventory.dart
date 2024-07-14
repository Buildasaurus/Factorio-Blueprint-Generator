import 'package:factorio_blueprint_generator/factorio_item_selector.dart';
import 'package:flutter/material.dart';

class Inventory extends StatefulWidget {
  const Inventory({super.key});

  @override
  State<Inventory> createState() => _InventoryState();
}

class _InventoryState extends State<Inventory> {
  int currentIndex = 0;
  @override
  Widget build(BuildContext context) {
    return Column(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        Wrap(
          spacing: 10, // Horizontal spacing between children
          children: List.generate(5, (index) {
            return ElevatedButton(
              child: Text(index.toString()),
              onPressed: () => setState(() => currentIndex = index),
            );
          }),
        ),
        SizedBox(
          height: 400,
          width: 400,
          child: FactorioItemSelector(
            inventoryIndex: currentIndex,
          ),
        )
      ],
    );
  }
}
