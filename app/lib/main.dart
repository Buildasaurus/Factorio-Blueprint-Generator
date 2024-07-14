
import 'package:factorio_blueprint_generator/factorio_item_selector.dart';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

//Taken from https://github.com/teoxoy/factorio-blueprint-editor/blob/master/packages/editor/src/core/factorioData.ts
// and converted to dart by Chat-GPT

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      home: Scaffold(
        appBar: AppBar(title: const Text('Flutter HTTP Example')),
        body: const Center(
          child: MyHomePage(),
        ),
      ),
    );
  }
}

class MyHomePage extends StatefulWidget {
  const MyHomePage({super.key});

  @override
  State<MyHomePage> createState() => _MyHomePageState();
}

class _MyHomePageState extends State<MyHomePage> {
  String _response = '';

  Future<void> _sendRequest(String request) async {
    try {
      final response = await http.post(
        Uri.parse('http://localhost:5000/process'),
        headers: <String, String>{
          'Content-Type': 'application/json; charset=UTF-8',
        },
        body: jsonEncode(<String, String>{
          'input_string': request,
        }),
      );

      if (response.statusCode == 200) {
        setState(() {
          _response = jsonDecode(response.body)['output_string'];
        });
      } else {
        setState(() {
          _response = 'Error: ${response.statusCode}';
        });
      }
    } catch (e) {
      setState(() {
        _response = "Remember to open the server: Error: $e";
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      mainAxisAlignment: MainAxisAlignment.center,
      children: <Widget>[
        ElevatedButton(
          onPressed: () => _sendRequest("Generate electric circuit"),
          child: const Text('Generate electric circuit'),
        ),
        const SizedBox(height: 10),
        ElevatedButton(
          onPressed: () => _sendRequest("Generate mall"),
          child: const Text('Generate mall'),
        ),
        const SizedBox(height: 20),
        SelectableText('Blueprint generator response: $_response'),

        //Item Selector
        const SizedBox(
          height: 400,
          width: 400,
          child: FactorioItemSelector(inventoryIndex: 0,),
        )
      ],
    );
  }
}
