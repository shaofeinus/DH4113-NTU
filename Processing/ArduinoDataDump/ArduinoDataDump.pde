import processing.serial.*;

String portName = "COM5";
Serial myPort;  // Create object from Serial class
int val[];      // Data received from the serial port
int offset = 0;

int dataSize[] = {1, 8, 8, 1,
                  5, 1, 1, 3,
                  4, 4, 1, 1,
                  1, 1, 1, 1};
                    
int a_time, a_x, a_y, a_z;
int m_time, m_x, m_y, m_z;
int ba_time, ba_p;
int ir_time, ir_dist;
int us_time, us_dist;
int start_count;
float a_hz, m_hz, ba_hz, ir_hz, us_hz;
Date last_start;

void setup() 
{
  val = new int[16];
  size(400, 200);
  offset = 0;
  start_count = 0;
  myPort = new Serial(this, portName, 115200);
  last_start = null;
}

void draw()
{
  background(0);
  textSize(14);
  
  text(a_time, 50, 50);
  text(a_x, 110, 50);
  text(a_y, 170, 50);
  text(a_z, 230, 50);
  text(a_hz + "hz", 290, 50);
  
  text(m_time, 50, 70);
  text(m_x, 110, 70);
  text(m_y, 170, 70);
  text(m_z, 230, 70);
  text(m_hz + "hz", 290, 70);
  
  text(ba_time, 50, 90);
  text((float)ba_p/4096, 110, 90);
  text(ba_hz + "hz", 290, 90);
  
  text(ir_time, 50, 110);
  text(ir_dist, 110, 110);
  text(ir_hz + "hz", 290, 110);
  
  text(us_time, 50, 130);
  text(us_dist, 110, 130);
  text(us_hz + "hz", 290, 130);
  
  text(start_count, 50, 150);
  
  if (last_start != null) 
    text(last_start.toString(), 110, 150);
}

void serialEvent(Serial thisPort) {
   int last, time;
   if ( myPort.available() > 0) {  // If data is available,
    val[offset] = myPort.read();         // read it and store it in val
    offset++;
    if (offset == dataSize[val[0]>>4]) {
      offset = 0;
      switch (val[0]>>4) {
        case 1:
          last = a_time;
          time = ((val[0]&0x0F)<<8)|val[1];
          if (time < last)
            last = ((time|0x1000)-last);
          else
            last =(time-last);
          a_hz = 1000.0/last;
          a_time = time;
          a_x = ((val[2]>>7 == 1)?0xFFFF0000:0)|val[2]<<8|val[3];
          a_y = ((val[4]>>7 == 1)?0xFFFF0000:0)|val[4]<<8|val[5];
          a_z = ((val[6]>>7 == 1)?0xFFFF0000:0)|val[6]<<8|val[7];
          break;
        case 2:
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
        case 7:
          if (val[0] == 's' && val[1] == '\r' && val[2] == '\n')
          {
            start_count++;
            last_start = new Date();
          }
          break;
        case 8:
          last = ir_time;
          time = ((val[0]&0x0F)<<8)|val[1];
          if (time < last)
            last = ((time|0x1000)-last);
          else
            last =(time-last);
          ir_hz = 1000.0/last;
          ir_time = time;
          ir_dist = val[2]<<8|val[3];
          break;
        case 9:
          last = us_time;
          time = ((val[0]&0x0F)<<8)|val[1];
          if (time < last)
            last = ((time|0x1000)-last);
          else
            last =(time-last);
          us_hz = 1000.0/last;
          us_time = time;
          us_dist = val[2]<<8|val[3];
          break;
        default:
          break;
      }
    }
  }
}
