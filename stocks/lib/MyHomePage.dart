import 'dart:async';

import 'package:chaquopy/chaquopy.dart';
import 'package:flutter/material.dart';
import 'package:locally/locally.dart';

class MyHomePage extends StatefulWidget {
  final rsi;

  const MyHomePage({Key? key, this.rsi = 0.0}) : super(key: key);

  @override
  _MyHomePageState createState() => _MyHomePageState();
}

class _MyHomePageState extends State<MyHomePage> {
  double rsi = 0.0;
  getRSI() async {
    String code = """
import bs4
import requests 
from bs4 import BeautifulSoup
    
    
url = 'https://in.investing.com/indices/s-p-cnx-nifty-technical?timeFrame=60'
headers={'User-Agent': 'Mozilla/5.0'}
data = requests.get(url, headers=headers)
 
soup = bs4.BeautifulSoup(data.content)
# print(soup.encode("utf-8"))
rsi = soup.find('td',{'class':'col-amount u-txt-align-end'}).find('span').text
print(rsi)
    """;

    var result = await Chaquopy.executeCode(code);
    return result['textOutput'];
    // return int.parse(result['textOutput']);
  }

  void notify() async {
    Timer.periodic(Duration(minutes: 1), (timer) {
      getRSI().then((value) {
        var newRsi;
        newRsi = double.parse(value);
        if (rsi != newRsi) {
          setState(() {
            rsi = newRsi;
          });

          Locally locally = Locally(
            context: context,
            payload: 'test',
            pageRoute:
                MaterialPageRoute(builder: (context) => MyHomePage(rsi: rsi)),
            appIcon: 'mipmap/ic_launcher',
          );

          if (rsi > 75) {
            locally.show(
              title: "Nifty 50 overbought",
              message: "Raised above 75 with RSI $rsi",
            );
          } else if (rsi < 25) {
            locally.show(
              title: "Nifty 50 oversold",
              message: "Dipped below 25 with RSI $rsi",
            );
          }
        }
      });
    });
  }

  @override
  Widget build(BuildContext context) {
    notify();
    return Scaffold(
      appBar: AppBar(
        title: Text("Home"),
      ),
      body: Container(
        child: Center(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Text("RSI",
                  style: TextStyle(fontSize: 40, fontWeight: FontWeight.bold)),
              Text(rsi.toString(), style: TextStyle(fontSize: 40)),
            ],
          ),
        ),
      ),
    );
  }
}
