package com.hdu.neurostudent_signalflow.devicelister.mindtooth;

import com.hdu.neurostudent_signalflow.config.MindToothProperties;
import com.hdu.neurostudent_signalflow.utils.mindtooth.LSL;
import com.hdu.neurostudent_signalflow.utils.websocket.MindtoothWebSocketClient;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Component;

import javax.annotation.Resource;
import java.util.Arrays;
import java.util.concurrent.BlockingQueue;

/*
*   功能：用于监测Mindtooth的阻抗值数据流动
* */
@Component
public class MindToothImpLister implements Runnable{
    private static final Logger logger = LoggerFactory.getLogger(MindToothImpLister.class);

    private static double lastTimeStamp;

    @Resource
    MindToothProperties mindToothProperties;    //mindtooth配置类

    @Resource
    private MindtoothWebSocketClient mindtoothWebSocketClient;

    BlockingQueue<double[]> recvData;   //接收队列
    // 数据和阻抗值用同一个队列
    public void setRecQueue(BlockingQueue<double[]> recQueue) {
        this.recvData = recQueue;
    }
    @Override
    public void run() {
        MindTooth_Impedance_lister();
    }

    public void MindTooth_Impedance_lister(){
        logger.info("mindtooth阻抗值监听程序启动...");
        try {
            lastTimeStamp = 0.0;
            LSL.StreamInfo[] results = LSL.resolve_stream("name",mindToothProperties.getImpedance_name());

            // 初始化数据流
            LSL.StreamInlet inlet = new LSL.StreamInlet(results[0]);

            // 存储数据
            int size = inlet.info().channel_count();
            double[] sample = new double[size];
            double[] timestamp = new double[1];
            double[] data = new double[size+2];

            while (true) {
                inlet.pull_chunk(sample, timestamp, 0.0);
                if (timestamp[0] == 0.0 || lastTimeStamp == timestamp[0]) {
                    continue;
                }
                lastTimeStamp = timestamp[0];

                //sample复制到data数组中
                System.arraycopy(sample,0,data,0,size);

                //data数组中倒数第二个值表示当前的数据是阻抗值还是数据
                data[size] = mindToothProperties.getImpedance_id();
                //data最后一个值表示当前的时间戳
                data[size+1] = System.currentTimeMillis();
                //将数据存储到该队列中
                recvData.add(data);

//                mindtoothWebSocketClient.send(Arrays.toString(sample));
            }
        } catch(Exception e) {
            logger.error("mindtooth阻抗值监听程序异常..." + e);
        }
    }
}
