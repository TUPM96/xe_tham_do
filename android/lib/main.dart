import 'dart:io';
import 'dart:async';
import 'package:flutter/material.dart';
import 'package:flutter_joystick/flutter_joystick.dart';
import 'package:flutter_mjpeg/flutter_mjpeg.dart';

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
  String status = "Đang chờ điều khiển...";
  DieuKhienMode mode = DieuKhienMode.thuCong;
  List<String> khoList = [];
  int? kho1Index;
  int? kho2Index;
  TextEditingController ipController = TextEditingController(text: "192.168.31.10");
  bool isConnected = false;

  Socket? socket;
  StreamSubscription? socketSubscription;
  String? currentIp; // Lưu IP đang kết nối để render video

  void onJoystickChange(StickDragDetails details) {
    if (isConnected && socket != null) {
      int leftMotor = (details.y * 100 - details.x * 50).toInt();
      int rightMotor = (details.y * 100 + details.x * 50).toInt();
      leftMotor = leftMotor.clamp(-100, 100);
      rightMotor = rightMotor.clamp(-100, 100);
      String cmd = "o $leftMotor $rightMotor";
      socket!.write(cmd + "\n");
      setState(() {
        status = "Đã gửi: $cmd";
      });
    }
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
      status = "Đang di chuyển đến kho $soKho...";
    });
    if (isConnected && socket != null) {
      socket!.write("GOTO_KHO $soKho\n");
    }
  }

  void ketNoiServer() async {
    try {
      final ip = ipController.text.trim();
      final s = await Socket.connect(ip, 3000, timeout: Duration(seconds: 5));
      socket = s;
      socketSubscription = s.listen((data) {
        final resp = String.fromCharCodes(data);
        // Có thể cập nhật trạng thái/phản hồi ở đây nếu muốn
      }, onDone: () {
        setState(() {
          isConnected = false;
          status = "Mất kết nối tới server";
          currentIp = null;
        });
        socket = null;
      }, onError: (e) {
        setState(() {
          isConnected = false;
          status = "Lỗi socket: $e";
          currentIp = null;
        });
        socket = null;
      });

      setState(() {
        isConnected = true;
        currentIp = ip;
        status = "Đã kết nối tới $ip";
      });
    } catch (e) {
      setState(() {
        status = "Kết nối thất bại: $e";
        isConnected = false;
        currentIp = null;
      });
    }
  }

  void ngatKetNoi() async {
    await socketSubscription?.cancel();
    await socket?.close();
    setState(() {
      isConnected = false;
      currentIp = null;
      status = "Đã ngắt kết nối";
    });
  }

  @override
  void dispose() {
    socket?.close();
    socketSubscription?.cancel();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Xe Tham Do')),
      body: Column(
        children: [
          // Phần nhập ip và kết nối/ngắt
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
            child: Row(
              children: [
                Expanded(
                  child: TextField(
                    controller: ipController,
                    decoration: InputDecoration(
                      labelText: "Nhập địa chỉ IP",
                      border: OutlineInputBorder(),
                      isDense: true,
                    ),
                  ),
                ),
                SizedBox(width: 8),
                isConnected
                    ? ElevatedButton(
                  onPressed: ngatKetNoi,
                  style: ElevatedButton.styleFrom(backgroundColor: Colors.red),
                  child: Text("Ngắt kết nối"),
                )
                    : ElevatedButton(
                  onPressed: ketNoiServer,
                  child: Text("Kết nối"),
                ),
              ],
            ),
          ),
          // 2 khung camera bên trên
          Row(
            children: [
              Expanded(
                child: CameraBox(
                  title: "Camera 1",
                  videoIp: currentIp,
                  isVideo: true,
                ),
              ),
              Expanded(
                child: CameraBox(
                  title: "Camera 2",
                  imageUrl: "https://i.imgur.com/u3zRr1l.png",
                  isVideo: false,
                ),
              ),
            ],
          ),
          // Map nhỏ lại
          Container(
            margin: EdgeInsets.symmetric(vertical: 8),
            height: 110,
            child: MapBox(),
          ),
          // Nút lựa chọn chế độ ở trên joystick
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
                  child: Text('Thủ Công'),
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
                  child: Text('Tự Động'),
                ),
              ],
            ),
          ),
          // Vùng điều khiển
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
                    // Nửa trái là joystick
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
                    // Nửa phải là các nút
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
                                child: Text('Thêm Kho 1'),
                              ),
                              SizedBox(width: 8),
                              ElevatedButton(
                                onPressed: () => themKho(2),
                                child: Text('Thêm Kho 2'),
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
                                child: Text('Đi chuyển đến kho 1'),
                              ),
                              SizedBox(width: 8),
                              ElevatedButton(
                                onPressed: kho2Index != null
                                    ? () => diChuyenDenKho(2)
                                    : null,
                                child: Text('Đi chuyển đến kho 2'),
                              ),
                            ],
                          ),
                          if (khoList.isNotEmpty)
                            Padding(
                              padding: EdgeInsets.only(top: 10),
                              child: Text(
                                "Danh sách kho: ${khoList.join(', ')}",
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

// CameraBox: nếu isVideo == true và có videoIp, show stream webcam, ngược lại show ảnh thường
class CameraBox extends StatelessWidget {
  final String title;
  final String? videoIp;
  final String? imageUrl;
  final bool isVideo;

  const CameraBox({
    required this.title,
    this.videoIp,
    this.imageUrl,
    this.isVideo = false,
  });

  @override
  Widget build(BuildContext context) {
    String? streamUrl;
    if (isVideo && videoIp != null) {
      streamUrl = "http://$videoIp:5000/video";
    }
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
              child: (isVideo && streamUrl != null)
                  ? Mjpeg(
                stream: streamUrl,
                isLive: true,
                error: (context, error, stack) {
                  return Center(child: Icon(Icons.videocam_off, color: Colors.red, size: 48));
                },
              )
                  : Image.network(
                imageUrl ?? "",
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
        "BẢN ĐỒ (Tích hợp google_maps_flutter hoặc flutter_map tại đây)",
        textAlign: TextAlign.center,
        style: TextStyle(fontSize: 16, color: Colors.green),
      ),
    );
  }
}