class InventoryLayoutGroup {
  String name;
  String icon;
  List<Icon>? icons;
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
    List<Icon>? icons = iconsList?.map((iconJson) => Icon.fromJson(iconJson)).toList();

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
    List<InventoryLayoutItem> items =
        itemList.map((itemJson) => InventoryLayoutItem.fromJson(itemJson)).toList();

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
  List<Icon>? icons;
  String order;

  InventoryLayoutItem({
    required this.name,
    this.icon,
    this.icons,
    required this.order,
  });

  factory InventoryLayoutItem.fromJson(Map<String, dynamic> json) {
    List<dynamic>? iconsList = json['icons'];
    List<Icon>? icons = iconsList?.map((iconJson) => Icon.fromJson(iconJson)).toList();

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

class Icon {
  String icon;
  int? iconSize;
  int? iconMimmaps;
  String? darkBackgroundIcon;
  ColorWithAlpha? tint;
  double? scale;
  List<int>? shift;

  Icon({
    required this.icon,
    this.iconSize,
    this.iconMimmaps,
    this.darkBackgroundIcon,
    this.tint,
    this.scale,
    this.shift,
  });

  factory Icon.fromJson(Map<String, dynamic> json) {
    return Icon(
      icon: json['icon'],
      iconSize: json['icon_size'],
      iconMimmaps: json['icon_mipmaps'],
      darkBackgroundIcon: json['dark_background_icon'],
      tint: json['tint'] != null ? ColorWithAlpha.fromJson(json['tint']) : null,
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
      'tint': tint?.toJson(),
      'scale': scale,
      'shift': shift,
    };
  }
}

class ColorWithAlpha {
  num red;
  num green;
  num blue;
  num? alpha;

  ColorWithAlpha({
    required this.red,
    required this.green,
    required this.blue,
    required this.alpha,
  });

  factory ColorWithAlpha.fromJson(Map<String, dynamic> json) {
    return ColorWithAlpha(
      red: json['r'],
      green: json['g'],
      blue: json['b'],
      alpha: json['a'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'red': red,
      'green': green,
      'blue': blue,
      'alpha': alpha,
    };
  }
}
