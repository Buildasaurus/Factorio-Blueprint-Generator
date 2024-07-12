import 'package:factorio_blueprint_generator/Resources.dart';
import 'package:flutter/material.dart';

class FactorioItemSelector extends StatelessWidget {
  const FactorioItemSelector({super.key});

  @override
  Widget build(BuildContext context) {
    final List<String> imageNames = [
      'assembling-machine-1',
      'cat',
      'boiler',
      'morecat',
    ];

    return GridView.builder(
      gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
        crossAxisCount: 2, // Adjust the number of columns as needed
        crossAxisSpacing: 8.0,
        mainAxisSpacing: 8.0,
      ),
      itemCount: imageNames.length,
      itemBuilder: (context, index) {
        return Image(
          image: Resources.instance.getImage(imageNames[index]),
          height: 100,
          width: 100,
        );
      },
    );
  }
}
