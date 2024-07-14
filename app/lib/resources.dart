import 'dart:collection';
import 'dart:io';

import 'package:flutter/material.dart';

class Resources{
  static Resources instance = Resources();
  final HashMap<String, AssetImage> _loadedImages = HashMap();

  Resources(){
    loadBaseImages();
  }
  void loadBaseImages(){

  }

  AssetImage getImage(String imagePath) {
    String path = "assets/factorio_icons/$imagePath";
    if (_loadedImages.containsKey(imagePath)){
      return _loadedImages[imagePath]!;
    }
    else{
      if(File(path).existsSync()){
        AssetImage image = AssetImage(path);
        _loadedImages[imagePath] = image;
        return image;
      }
      else{
        debugPrint("The image \"$imagePath\" could not be found");
        return const AssetImage("assets/ImageNotFound.png");
      }
    }
  }


}
