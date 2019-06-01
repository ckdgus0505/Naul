using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;
using OpenCvSharp;
using System.Net;
using System.Net.Sockets;
using MySql.Data.MySqlClient;
using System.Threading;

namespace Interface
{
    public partial class Form1 : Form
    {
        byte[] receive = new Byte[1024];

        string IP = "175.214.125.27";
        Int32 PORT = 9009;
        bool checking = false; // 사람이 인식되고 있음을 나타내는 변수
  


        IplImage haarface;
        CvCapture capture;
        IplImage src;
        public Form1()
        {
            InitializeComponent();
        }


        private void DataGridView1_CellContentClick(object sender, DataGridViewCellEventArgs e)
        {

        }

        private void Timer1_Tick(object sender, EventArgs e)
        {
            src = capture.QueryFrame();

            pictureBoxIpl1.ImageIpl = FaceDetection(src);
        }

        private void camera_On()
        {
            try
            {
                capture = CvCapture.FromCamera(CaptureDevice.DShow, 0);
                capture.SetCaptureProperty(CaptureProperty.FrameWidth, 640);
                capture.SetCaptureProperty(CaptureProperty.FrameHeight, 360);


            }
            catch
            {
                timer1.Enabled = false;
            }
        }

        private void camera_Off()
        {
            //CvReleaseFunc(&capture);
        }

        private void Btn_att_start_Click(object sender, EventArgs e)
        {
            DBConnection();
            camera_On();
            MessageBox.Show("출석을 시작합니다.");
            timer1.Enabled = true;

        }

        private void Btn_spk_start_Click(object sender, EventArgs e)
        {
            String query = "SELECT * FROM ai.client_table;";
            MessageBox.Show("출석을 시작합니다.");
            DBConnection();

            String studentID = "201511061";

        }

        private void Btn_att_end_Click(object sender, EventArgs e)
        {
            src = null;
            timer1.Enabled = false;



            // while()
            //{
            //    send_number();
            //}
        }


        private void send_number() // 학번, 학수번호를 보내서 출석을 함
        {
            int length = 0;
            Socket sock = connection();

            try
            {
                Byte[] data = Encoding.Default.GetBytes("201511041ea0017_1");
                sock.Send(data);

                length = sock.Receive(receive);

                MessageBox.Show(Encoding.UTF8.GetString(receive));
            }
            catch (Exception err)
            {
                MessageBox.Show(err.ToString());
            }

            finally
            {
                sock.Close();
            }
        }

        private void send_class() // 학수번호를 보내서 해당 과목의 학생들을 받음  => DB 직접 접속해서 받아올것!
        {
            int length = 0;
            Socket sock = connection();

            try
            {

                Byte[] data = Encoding.Default.GetBytes("ea0017_1");
                sock.Send(data);

                length = sock.Receive(receive);

                MessageBox.Show(Encoding.UTF8.GetString(receive));
            }
            catch (Exception err)
            {
                MessageBox.Show(err.ToString());
            }

            finally
            {
                sock.Close();
            }
        }



        private void send_picture() // 사진을 보내서 해당하는 학번을 받음
        {
            int length = 0;
            Socket sock = connection();

            try
            {
                byte[] pic = src.ToBytes(".jpg");

                sock.Send(pic);
                length = sock.Receive(receive);

                String studentID = Encoding.UTF8.GetString(receive);

                if(studentID == "Undefined") // 사람 인식 못함
                {
                    checking = false;
                }
                else // 사람 인식 함
                {
                    if (MessageBox.Show(studentID + " 출석 하시겠습니까?", "", MessageBoxButtons.YesNo) == DialogResult.Yes)
                    {

                        String query = "UPDATE ai.client_table SET attend = 1 WHERE studentID = '" + studentID  + "';";
                        DBupdate(query);
                        DBConnection();
                        
                        MessageBox.Show("출석처리되었습니다.");
                        Thread.Sleep(1000);
                        checking = false;
                    }
                    else
                    {
                        checking = false;
                    }

                }
            }
            catch (Exception err)
            {
                MessageBox.Show(err.ToString());
            }

            finally
            {
                 sock.Close();
            }

        }
        private Socket connection()
        {
            //1. 접속할 종단점(서버측 소켓)생성
            IPAddress ip = IPAddress.Parse(IP);//인자값 : 서버측 IP
            IPEndPoint endPoint = new IPEndPoint(ip, PORT);//인자값 : IPAddress,포트번호

            //2. Tcp Socket 생성
            Socket sock = new Socket(AddressFamily.InterNetwork, SocketType.Stream, ProtocolType.Tcp);

            //3. 접속(전화걸기)
            
            sock.Connect(endPoint);

            return sock;
        }

        private void DBupdate(String query)
        {
            string constring = "datasource=isg1031.iptime.org;port=20050;username=aitester;password=aitester001!";
            MySqlConnection connection = new MySqlConnection(constring);
            MySqlCommand cmdDataBase = new MySqlCommand(query, connection);
            try
            {
                connection.Open();
                cmdDataBase.ExecuteNonQuery();
            }
            catch (Exception ex)
            {
                MessageBox.Show(ex.Message);
            }
            connection.Close();
        }
        private void DBConnection()
        {
            String query = "SELECT * FROM ai.client_table;";
            string constring = "datasource=isg1031.iptime.org;port=20050;username=aitester;password=aitester001!";
            MySqlConnection connection = new MySqlConnection(constring);

            MySqlCommand cmdDataBase = new MySqlCommand(query, connection);

            try
            {
                
                
                MySqlDataAdapter sda = new MySqlDataAdapter();
                sda.SelectCommand = cmdDataBase;
                DataTable dbdataset = new DataTable();

                sda.Fill(dbdataset);
                BindingSource BSource = new BindingSource();
                BSource.DataSource = dbdataset;
                dataGridView1.DataSource = BSource;
                sda.Update(dbdataset);
            }
            catch (Exception ex)
            {
                MessageBox.Show(ex.Message);
            }           
            connection.Close();
        }

        public IplImage FaceDetection(IplImage src)
        { // https://076923.github.io/posts/C-opencv-29/
            haarface = new IplImage(src.Size, BitDepth.U8, 3); // harrface 는 원본을 복사한 이미지
            Cv.Copy(src, haarface);

            const double scale = 0.9; // scale은 검출되는 이미지의 비율
            const double scaleFactor = 1.139; // 얼굴 검출시에 사용되는 상수
            const int minNeighbors = 1; // 얼굴 검출시에 사용되는 상수

            using (IplImage Detected_image = new IplImage(new CvSize(Cv.Round(src.Width / scale), Cv.Round(src.Height / scale)), BitDepth.U8, 1))
            { // 검출되는 이미지인 detected image 를 scale의 비율에 맞게 재조정 함
                using (IplImage gray = new IplImage(src.Size, BitDepth.U8, 1)) // 이미지의 크기를 조정
                {
                    Cv.CvtColor(src, gray, ColorConversion.BgrToGray);
                    Cv.Resize(gray, Detected_image, Interpolation.Linear);
                    Cv.EqualizeHist(Detected_image, Detected_image); // 이미지의 화상을 평탄화 (어둡고 밝은 부분이 조정됨)
                }

                using (CvHaarClassifierCascade cascade = CvHaarClassifierCascade.FromFile("../../haarcascade_frontalface_alt.xml"))
                using (CvMemStorage storage = new CvMemStorage()) // 메모리에 저장소 생성
                {
                    CvSeq<CvAvgComp> faces = Cv.HaarDetectObjects(Detected_image, cascade, storage, scaleFactor, minNeighbors, HaarDetectionType.FindBiggestObject, new CvSize(90, 90), new CvSize(0, 0));
                    // detected_image = 탐지할 이미지, cascade =  storage = 메모리가 저장될 저장소 , HarrDetectionType : 작동 모드 
                    if (faces.Total == 1 && checking == false)
                    {
                        checking = true;
                        send_picture();
    
                    }
                    for (int i = 0; i < faces.Total; i++)
                    {
                        CvRect r = faces[i].Value.Rect;
                        CvPoint center = new CvPoint
                        {
                            X = Cv.Round((r.X + r.Width * 0.5) * scale),
                            Y = Cv.Round((r.Y + r.Height * 0.5) * scale)
                        };
                        int radius = Cv.Round((r.Width + r.Height) * 0.25 * scale);
                        haarface.Circle(center, radius, CvColor.Black, 3, LineType.AntiAlias, 0);
                    }
                }

                return haarface;
            }
        }
    }
}
