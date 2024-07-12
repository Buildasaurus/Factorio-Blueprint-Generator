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

  AssetImage getImage(String imageName) {
    String path = "assets/factorio_icons/$imageName.png";
    if (_loadedImages.containsKey(imageName)){
      return _loadedImages[imageName]!;
    }
    else{
      if(File(path).existsSync()){
        AssetImage image = AssetImage(path);
        _loadedImages[imageName] = image;
        return image;
      }
      else{
        debugPrint("The image \"$imageName\" could not be found");
        return const AssetImage("assets/ImageNotFound.png");
      }

    }
  }


}
