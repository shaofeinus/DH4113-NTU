import processing.serial.*;
import java.util.*;

String portName = "COM5";
Serial myPort;  // Create object from Serial class
int[] val;      // Data received from the serial port
int offset = 0;

final int COUNT_IR = 2;
final int COUNT_US = 3;

final int[] dataSize = {
                  1, 8, 8, 1,
                  5, 4, 4, 4,
                  1, 1, 1, 4,
                  4, 4, 1, 1
                };
                  
LinkedList<Integer> reset_conditions;
LinkedList<Long> reset_times;
                    
int a_time, a_x, a_y, a_z, a_packets;
int m_time, m_x, m_y, m_z, m_packets;
int ba_time, ba_p, ba_packets;
float a_hz, m_hz, ba_hz;

int[] ir_time, ir_dist, ir_packets;
float[] ir_hz;
int[] us_time, us_dist, us_packets;
float[] us_hz;
int start_count;

Date last_start;

int[] additional_info;

void setup() 
{
  size(600, 300);
  ir_time = new int[4];
  ir_dist = new int[4];
  ir_packets = new int[4];
  ir_hz = new float[4];
  
  us_time = new int[4];
  us_dist = new int[4];
  us_packets = new int[4];
  us_hz = new float[4];
  
  reset_conditions = new LinkedList<Integer>();
  reset_times = new LinkedList<Long>();
  additional_info = new int[3];
  val = new int[16];
  
  offset = 0;
  start_count = 0;
  myPort = new Serial(this, portName, 115200);
  last_start = null;
}

void draw()
{
  long sec = 0;
  int i;
  int text_y;
  background(0);
  textSize(14);
  if (last_start != null) {
    sec = ((new Date()).getTime() - last_start.getTime())/1000;
  }
  text_y = 50;
  text("a", 20, text_y);
  text(a_time, 50, text_y);
  text(a_x, 110, text_y);
  text(a_y, 170, text_y);
  text(a_z, 230, text_y);
  text(a_hz + "hz", 290, text_y);
  text((float)a_packets/sec + "hz", 410, text_y);
  
  text_y += 20;
  text("m", 20, text_y);
  text(m_time, 50, text_y);
  text(m_x, 110, text_y);
  text(m_y, 170, text_y);
  text(m_z, 230, text_y);
  text(m_hz + "hz", 290, text_y);
  text((float)m_packets/sec + "hz", 410, text_y);
  
  text_y += 20;
  text("ba", 20, text_y);
  text(ba_time, 50, text_y);
  text((float)ba_p/4096, 110, text_y);
  text(ba_hz + "hz", 290, text_y);
  text((float)ba_packets/sec + "hz", 410, text_y);
  
  for (i = 0; i < COUNT_IR; ++i)
  {
    text_y += 20;
    text("ir" + (i+1), 20, text_y);
    text(ir_time[i], 50, text_y);
    text(ir_dist[i], 110, text_y);
    text(ir_hz[i] + "hz", 290, text_y);
    text((float)ir_packets[i]/sec + "hz", 410, text_y);
  }
  
  for (i = 0; i < COUNT_US; ++i)
  {
    text_y += 20;
    text("us" + (i+1), 20, text_y);
    text(us_time[i], 50, text_y);
    text(us_dist[i], 110, text_y);
    text(us_hz[i] + "hz", 290, text_y);
    text((float)us_packets[i]/sec + "hz", 410, text_y);
  }
  
  text_y += 20;
  text(start_count, 50, text_y);
  if (last_start != null) 
    text(last_start.toString(), 110, text_y);
    
  text_y += 20;  
  text(reset_conditions.toString(), 50, text_y);
  
  text_y += 20;
  text(reset_times.toString(), 50, text_y);
  
  text_y += 20;
  text(additional_info[0], 50, text_y); 
  text(additional_info[1], 110, text_y);
  text(additional_info[2], 170, text_y);
}

void serialEvent(Serial thisPort) {
   int last, time, temp, device;
   if ( myPort.available() > 0) {  // If data is available,
    val[offset] = myPort.read();         // read it and store it in val
    offset++;
    if (offset == dataSize[val[0]>>4]) {
      offset = 0;
      switch (val[0]>>4) {
        case 1:
          ++a_packets;
          temp = last = a_time;
          time = ((val[0]&0x0F)<<8)|val[1];
          if (time < last)
            last = ((time|0x1000)-last);
          else
            last = (time-last);
          a_hz = 1000.0/last;
          if (last > 10)
          {
            additional_info[0] = last;
            additional_info[1] = temp;
            additional_info[2] = time;
          }
          a_time = time;
          a_x = ((val[2]>>7 == 1)?0xFFFF0000:0)|val[2]<<8|val[3];
          a_y = ((val[4]>>7 == 1)?0xFFFF0000:0)|val[4]<<8|val[5];
          a_z = ((val[6]>>7 == 1)?0xFFFF0000:0)|val[6]<<8|val[7];
          break;
        case 2:
          ++m_packets;
          last = m_time;
          time = ((val[0]&0x0F)<<8)|val[1];
          if (time < last)
            last = ((time|0x1000)-last);
          else
            last =(time-last);
          m_hz = 1000.0/last;
          m_time = time;
          m_x = ((val[2]>>7 == 1)?0xFFFF0000:0)|val[2]<<8|val[3];
          m_y = ((val[4]>>7 == 1)?0xFFFF0000:0)|val[4]<<8|val[5];
          m_z = ((val[6]>>7 == 1)?0xFFFF0000:0)|val[6]<<8|val[7];
          break;
        case 4:
          ++ba_packets;
          last = ba_time;
          time = ((val[0]&0x0F)<<8)|val[1];
          if (time < last)
            last = ((time|0x1000)-last);
          else
            last =(time-last);
          ba_hz = 1000.0/last;
          ba_time = time;
          ba_p = val[2]<<16|val[3]<<8|val[4];
          break;
        case 5:
          if (val[0] == 'S' && val[2] == '\r' && val[3] == '\n')
          {
            a_packets = m_packets = ba_packets = 0;
            for (int i = 0; i < 4; ++i)
            {
              ir_packets[i] = us_packets[i] = 0;
            }
            reset_conditions.add(val[1]);
            start_count++;
            last_start = new Date();
            reset_times.add(last_start.getTime());
          }
          break;
        case 6:
        case 7:
          device = (val[0]>>4)-6;
          ++ir_packets[device];
          last = ir_time[device];
          time = ((val[0]&0x0F)<<8)|val[1];
          if (time < last)
            last = ((time|0x1000)-last);
          else
            last =(time-last);
          ir_hz[device] = 1000.0/last;
          ir_time[device] = time;
          ir_dist[device] = val[2]<<8|val[3];
          break;
        case 11:
        case 12:
        case 13:
          device = (val[0]>>4)-11;
          ++us_packets[device];
          last = us_time[device];
          time = ((val[0]&0x0F)<<8)|val[1];
          if (time < last)
            last = ((time|0x1000)-last);
          else
            last =(time-last);
          us_hz[device] = 1000.0/last;
          us_time[device] = time;
          us_dist[device] = val[2]<<8|val[3];
          break;
        default:
          break;
      }
    }
  }
}