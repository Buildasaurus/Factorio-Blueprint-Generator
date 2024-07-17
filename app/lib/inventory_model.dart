import 'dart:ui';

class InventoryLayoutGroup {
  String name;
  String icon;
  List<IconInfo>? icons;
  int? iconSize;
  int? iconMipMaps;
  String order;
  List<InventoryLayoutSubgroup> subgroups;
  String localisedName;

  InventoryLayoutGroup({
    required this.name,
    required this.icon,
    this.icons,
    this.iconSize,
    this.iconMipMaps,
    required this.order,
    required this.subgroups,
    required this.localisedName,
  });

  factory InventoryLayoutGroup.fromJson(Map<String, dynamic> json) {
    List<dynamic> subgroupList = json['subgroups'] ?? [];
    List<InventoryLayoutSubgroup> subgroups = subgroupList
        .map((subgroupJson) => InventoryLayoutSubgroup.fromJson(subgroupJson))
        .toList();

    List<dynamic>? iconsList = json['icons'];
    List<IconInfo>? icons =
        iconsList?.map((iconJson) => IconInfo.fromJson(iconJson)).toList();

    return InventoryLayoutGroup(
      name: json['name'],
      icon: json['icon'],
      icons: icons,
      iconSize: json['icon_size'],
      iconMipMaps: json['icon_mipmaps'],
      order: json['order'],
      subgroups: subgroups,
      localisedName: json['localised_name'],
    );
  }

  Map<String, dynamic> toJson() {
    List<Map<String, dynamic>> subgroupsJson =
        subgroups.map((subgroup) => subgroup.toJson()).toList();

    List<Map<String, dynamic>>? iconsJson =
        icons?.map((icon) => icon.toJson()).toList();

    return {
      'name': name,
      'icon': icon,
      'icons': iconsJson,
      'icon_size': iconSize,
      'icon_mipmaps': iconMipMaps,
      'order': order,
      'subgroups': subgroupsJson,
      'localised_name': localisedName,
    };
  }
}

class InventoryLayoutSubgroup {
  String name;
  String order;
  List<InventoryLayoutItem> items;

  InventoryLayoutSubgroup({
    required this.name,
    required this.order,
    required this.items,
  });

  factory InventoryLayoutSubgroup.fromJson(Map<String, dynamic> json) {
    List<dynamic> itemList = json['items'] ?? [];
    List<InventoryLayoutItem> items = itemList
        .map((itemJson) => InventoryLayoutItem.fromJson(itemJson))
        .toList();

    return InventoryLayoutSubgroup(
      name: json['name'],
      order: json['order'],
      items: items,
    );
  }

  Map<String, dynamic> toJson() {
    List<Map<String, dynamic>> itemsJson =
        items.map((item) => item.toJson()).toList();

    return {
      'name': name,
      'order': order,
      'items': itemsJson,
    };
  }
}

class InventoryLayoutItem {
  String name;
  String? icon;
  List<IconInfo>? icons;
  String order;

  InventoryLayoutItem({
    required this.name,
    this.icon,
    this.icons,
    required this.order,
  });

  factory InventoryLayoutItem.fromJson(Map<String, dynamic> json) {
    List<dynamic>? iconsList = json['icons'];
    List<IconInfo>? icons =
        iconsList?.map((iconJson) => IconInfo.fromJson(iconJson)).toList();

    return InventoryLayoutItem(
      name: json['name'],
      icon: json['icon'],
      icons: icons,
      order: json['order'],
    );
  }

  Map<String, dynamic> toJson() {
    List<Map<String, dynamic>>? iconsJson =
        icons?.map((icon) => icon.toJson()).toList();

    return {
      'name': name,
      'icon': icon,
      'icons': iconsJson,
      'order': order,
    };
  }
}

class IconInfo {
  String icon;
  int? iconSize;
  int? iconMimmaps;
  String? darkBackgroundIcon;
  Color? tint;
  double? scale;
  List<int>? shift;

  IconInfo({
    required this.icon,
    this.iconSize,
    this.iconMimmaps,
    this.darkBackgroundIcon,
    this.tint,
    this.scale,
    this.shift,
  });

  factory IconInfo.fromJson(Map<String, dynamic> json) {
    return IconInfo(
      icon: json['icon'],
      iconSize: json['icon_size'],
      iconMimmaps: json['icon_mipmaps'],
      darkBackgroundIcon: json['dark_background_icon'],
      tint: json['tint'] != null ? colorFromJson(json['tint']) : null,
      scale: json['scale'],
      shift: json['shift']?.cast<int>(),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'icon': icon,
      'icon_size': iconSize,
      'icon_mipmaps': iconMimmaps,
      'dark_background_icon': darkBackgroundIcon,
      'tint': colorToJson(tint),
      'scale': scale,
      'shift': shift,
    };
  }

  static Color colorFromJson(Map<String, dynamic> json) {
    return Color.fromARGB(
        (json['a'] != null ? json['a'] * 255 : 255.0).round(),
        (json['r'] * 255).round(),
        (json['g'] * 255).round(),
        (json['b'] * 255).round());
  }

  Map<String, dynamic>? colorToJson(Color? color) {
    if (color == null) return null;
    return {
      'red': color.red / 255,
      'green': color.green / 255,
      'blue': color.blue / 255,
      'alpha': color.alpha / 255,
    };
  }
}
