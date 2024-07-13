class InventoryLayoutGroup {
  String name;
  String icon;
  List<Icon>? icons;
  int? icon_size;
  int? icon_mipmaps;
  String order;
  List<InventoryLayoutSubgroup> subgroups;
  String localised_name;

  InventoryLayoutGroup({
    required this.name,
    required this.icon,
    this.icons,
    this.icon_size,
    this.icon_mipmaps,
    required this.order,
    required this.subgroups,
    required this.localised_name,
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
      icon_size: json['icon_size'],
      icon_mipmaps: json['icon_mipmaps'],
      order: json['order'],
      subgroups: subgroups,
      localised_name: json['localised_name'],
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
      'icon_size': icon_size,
      'icon_mipmaps': icon_mipmaps,
      'order': order,
      'subgroups': subgroupsJson,
      'localised_name': localised_name,
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
  int? icon_size;
  int? icon_mipmaps;
  String? dark_background_icon;
  ColorWithAlpha? tint;
  double? scale;
  List<int>? shift;

  Icon({
    required this.icon,
    this.icon_size,
    this.icon_mipmaps,
    this.dark_background_icon,
    this.tint,
    this.scale,
    this.shift,
  });

  factory Icon.fromJson(Map<String, dynamic> json) {
    return Icon(
      icon: json['icon'],
      icon_size: json['icon_size'],
      icon_mipmaps: json['icon_mipmaps'],
      dark_background_icon: json['dark_background_icon'],
      tint: json['tint'] != null ? ColorWithAlpha.fromJson(json['tint']) : null,
      scale: json['scale'],
      shift: json['shift']?.cast<int>(),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'icon': icon,
      'icon_size': icon_size,
      'icon_mipmaps': icon_mipmaps,
      'dark_background_icon': dark_background_icon,
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
