import 'package:flutter/material.dart';
import 'package:flutter_joystick/flutter_joystick.dart';

void main() {
  runApp(MyApp());
}

class MyApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Xe Tham Do',
      theme: ThemeData(primarySwatch: Colors.blue),
      home: XeThamDoScreen(),
      debugShowCheckedModeBanner: false,
    );
  }
}

enum DieuKhienMode { thuCong, tuDong }

class XeThamDoScreen extends StatefulWidget {
  @override
  _XeThamDoScreenState createState() => _XeThamDoScreenState();
}

class _XeThamDoScreenState extends State<XeThamDoScreen> {
  String status = "Dang cho dieu khien...";
  DieuKhienMode mode = DieuKhienMode.thuCong;
  List<String> khoList = [];
  int? kho1Index;
  int? kho2Index;
  TextEditingController ipController = TextEditingController(text: "192.168.31.10");
  bool isConnected = false;

  void onJoystickChange(StickDragDetails details) {
    // Xu ly dieu khien o day
  }

  void themKho(int soKho) {
    setState(() {
      String tenKho = "Kho $soKho";
      if (!khoList.contains(tenKho)) {
        khoList.add(tenKho);
        if (soKho == 1) kho1Index = khoList.length - 1;
        if (soKho == 2) kho2Index = khoList.length - 1;
      }
    });
  }

  void diChuyenDenKho(int soKho) {
    setState(() {
      status = "Dang di chuyen den kho $soKho...";
      // Gui lenh di chuyen den kho tu dong
    });
  }

  void ketNoiServer() {
    setState(() {
      isConnected = true; // Ban co the thay bang logic ket noi thuc te
      status = "Da ket noi toi ${ipController.text}";
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Xe Tham Do')),
      body: Column(
        children: [
          // Phan nhap ip va ket noi
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
            child: Row(
              children: [
                Expanded(
                  child: TextField(
                    controller: ipController,
                    decoration: InputDecoration(
                      labelText: "Nhap dia chi IP",
                      border: OutlineInputBorder(),
                      isDense: true,
                    ),
                  ),
                ),
                SizedBox(width: 8),
                ElevatedButton(
                  onPressed: isConnected ? null : ketNoiServer,
                  child: Text(isConnected ? "Da ket noi" : "Ket noi"),
                ),
              ],
            ),
          ),
          // 2 khung camera ben tren
          Row(
            children: [
              Expanded(
                child: CameraBox(
                  title: "Webcam",
                  imageUrl: "https://placekitten.com/400/300",
                ),
              ),
              Expanded(
                child: CameraBox(
                  title: "Camera Nhiet",
                  imageUrl: "https://i.imgur.com/u3zRr1l.png",
                ),
              ),
            ],
          ),
          // Map nho lai
          Container(
            margin: EdgeInsets.symmetric(vertical: 8),
            height: 110, // map nho lai
            child: MapBox(),
          ),
          // Nut lua chon che do o tren joystick
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                ElevatedButton(
                  style: ElevatedButton.styleFrom(
                    backgroundColor: mode == DieuKhienMode.thuCong
                        ? Colors.blue
                        : Colors.grey[300],
                    foregroundColor: mode == DieuKhienMode.thuCong
                        ? Colors.white
                        : Colors.black,
                  ),
                  onPressed: () {
                    setState(() {
                      mode = DieuKhienMode.thuCong;
                    });
                  },
                  child: Text('Thu Cong'),
                ),
                SizedBox(width: 16),
                ElevatedButton(
                  style: ElevatedButton.styleFrom(
                    backgroundColor: mode == DieuKhienMode.tuDong
                        ? Colors.blue
                        : Colors.grey[300],
                    foregroundColor: mode == DieuKhienMode.tuDong
                        ? Colors.white
                        : Colors.black,
                  ),
                  onPressed: () {
                    setState(() {
                      mode = DieuKhienMode.tuDong;
                    });
                  },
                  child: Text('Tu Dong'),
                ),
              ],
            ),
          ),
          // Vung dieu khien
          if (mode == DieuKhienMode.thuCong)
            Padding(
              padding: EdgeInsets.only(bottom: 18),
              child: Column(
                children: [
                  Text(status, style: TextStyle(fontSize: 16)),
                  SizedBox(height: 8),
                  Joystick(
                    mode: JoystickMode.all,
                    listener: onJoystickChange,
                    base: Container(
                      width: 120,
                      height: 120,
                      decoration: BoxDecoration(
                        shape: BoxShape.circle,
                        color: Colors.grey[300],
                      ),
                    ),
                    stick: Container(
                      width: 50,
                      height: 50,
                      decoration: BoxDecoration(
                        shape: BoxShape.circle,
                        color: Colors.blue,
                      ),
                    ),
                  ),
                ],
              ),
            ),
          if (mode == DieuKhienMode.tuDong)
            Padding(
              padding: EdgeInsets.only(bottom: 18),
              child: Container(
                height: 180,
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    // Nua trai la joystick
                    Expanded(
                      flex: 1,
                      child: Column(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          Text(status, style: TextStyle(fontSize: 16)),
                          SizedBox(height: 8),
                          Joystick(
                            mode: JoystickMode.all,
                            listener: onJoystickChange,
                            base: Container(
                              width: 120,
                              height: 120,
                              decoration: BoxDecoration(
                                shape: BoxShape.circle,
                                color: Colors.grey[300],
                              ),
                            ),
                            stick: Container(
                              width: 50,
                              height: 50,
                              decoration: BoxDecoration(
                                shape: BoxShape.circle,
                                color: Colors.blue,
                              ),
                            ),
                          ),
                        ],
                      ),
                    ),
                    // Nua phai la cac nut
                    Expanded(
                      flex: 1,
                      child: Column(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          Row(
                            mainAxisAlignment: MainAxisAlignment.center,
                            children: [
                              ElevatedButton(
                                onPressed: () => themKho(1),
                                child: Text('Them Kho 1'),
                              ),
                              SizedBox(width: 8),
                              ElevatedButton(
                                onPressed: () => themKho(2),
                                child: Text('Them Kho 2'),
                              ),
                            ],
                          ),
                          SizedBox(height: 10),
                          Row(
                            mainAxisAlignment: MainAxisAlignment.center,
                            children: [
                              ElevatedButton(
                                onPressed: kho1Index != null
                                    ? () => diChuyenDenKho(1)
                                    : null,
                                child: Text('Di chuyen den kho 1'),
                              ),
                              SizedBox(width: 8),
                              ElevatedButton(
                                onPressed: kho2Index != null
                                    ? () => diChuyenDenKho(2)
                                    : null,
                                child: Text('Di chuyen den kho 2'),
                              ),
                            ],
                          ),
                          if (khoList.isNotEmpty)
                            Padding(
                              padding: EdgeInsets.only(top: 10),
                              child: Text(
                                "Danh sach kho: ${khoList.join(', ')}",
                                style: TextStyle(fontSize: 14, color: Colors.green),
                              ),
                            ),
                        ],
                      ),
                    ),
                  ],
                ),
              ),
            ),
        ],
      ),
    );
  }
}

class CameraBox extends StatelessWidget {
  final String title;
  final String imageUrl;

  const CameraBox({required this.title, required this.imageUrl});

  @override
  Widget build(BuildContext context) {
    return Container(
      height: 180,
      margin: EdgeInsets.all(8),
      decoration: BoxDecoration(
        border: Border.all(color: Colors.blueAccent),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Column(
        children: [
          Text(title, style: TextStyle(fontWeight: FontWeight.bold)),
          Expanded(
            child: ClipRRect(
              borderRadius: BorderRadius.circular(8),
              child: Image.network(
                imageUrl,
                fit: BoxFit.cover,
                width: double.infinity,
                errorBuilder: (_, __, ___) =>
                    Center(child: Icon(Icons.broken_image)),
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class MapBox extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        border: Border.all(color: Colors.green),
        borderRadius: BorderRadius.circular(12),
      ),
      alignment: Alignment.center,
      child: Text(
        "BAN DO (Tich hop google_maps_flutter hoac flutter_map tai day)",
        textAlign: TextAlign.center,
        style: TextStyle(fontSize: 16, color: Colors.green),
      ),
    );
  }
}