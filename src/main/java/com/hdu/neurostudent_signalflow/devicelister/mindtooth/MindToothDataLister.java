package com.hdu.neurostudent_signalflow.devicelister.mindtooth;

import com.hdu.neurostudent_signalflow.adapter.MindToothDeviceAdapter;
import com.hdu.neurostudent_signalflow.config.MindToothProperties;
import com.hdu.neurostudent_signalflow.utils.mindtooth.LSL;
import lombok.Setter;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Component;

import javax.annotation.PostConstruct;
import javax.annotation.Resource;
import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.file.StandardOpenOption;
import java.time.Instant;
import java.util.Arrays;
import java.util.concurrent.BlockingDeque;

/*
*   功能：用于监测mindtooth的数据流动
* */
@Component
public class MindToothDataLister implements Runnable {
    private static final Logger logger = LoggerFactory.getLogger(MindToothDataLister.class);

    private static double lastTimeStamp;

    @Resource
    MindToothProperties mindToothProperties;    //mindtooth配置类

    BlockingDeque<double[]> recvData;   //数据接收队列

    @Setter
    MindToothDeviceAdapter mindToothDeviceAdatper;

    // 数据和阻抗值监听程序用的是同一个数据接收队列
    public void setRecQueue(BlockingDeque<double[]> recQueue) {
        this.recvData = recQueue;
    }

    @PostConstruct
    private void init() {
        if (!mindToothProperties.isTestEnable()) {
            // 删除原来的测试文件
            Path path = Paths.get(mindToothProperties.getTestInputFile());
            try {
                Files.deleteIfExists(path);
                logger.info("mindtooth测试文件删除成功!");
            } catch (IOException e) {
                logger.error("mindtooth测试文件删除失败: {}", e.getMessage());
            }
        }
    }

    @Override
    public void run() {
        MindTooth_Data_lister();
    }

    // mindtooth-LSL数据流监听程序
    public void MindTooth_Data_lister(){
        logger.info("mindtooth数据监听程序启动...");
        try {
            lastTimeStamp = 0.0;
            LSL.StreamInfo[] results = LSL.resolve_stream("name",mindToothProperties.getData_name());

            // 初始化数据流
            LSL.StreamInlet inlet = new LSL.StreamInlet(results[0]);

            // 存储数据
            int size = inlet.info().channel_count();
            double[] sample = new double[size];
            double[] timestamp = new double[1];
            double[] data = new double[size+2];

            while (true) {
                inlet.pull_chunk(sample, timestamp, 0.0);
                if (timestamp[0] == 0.0){
                    continue;
                }
                if (lastTimeStamp == timestamp[0]) {
                    continue;
                }
                lastTimeStamp = timestamp[0];
                System.arraycopy(sample, 0, data, 0, size);

                //data数组中倒数第二个值表示当前的数据是阻抗值还是数据
                data[size] = mindToothProperties.getData_id(); //阻抗值为0,数据为1
                //data最后一个值表示当前的时间戳
                // 获取当前的 Instant
                Instant now = Instant.now();
                // 时间戳
                double currTimestamp = System.currentTimeMillis();
                data[size+1] = currTimestamp;

//                mindToothDeviceAdatper.processData(data);
                // 数据可靠性测试
                if (mindToothProperties.isTestEnable()) {
                    writeData2TestFile(data);
                }
                recvData.add(data);
            }

        } catch(Exception ex) {
            logger.error("mindtooth数据监听程序异常...", ex);
        }
    }

    private void writeData2TestFile(double[] data) {
        Path path = Paths.get(mindToothProperties.getTestInputFile());

        try {
            Files.createDirectories(path.getParent());
            if (!Files.exists(path)) {
                Files.createFile(path);
                logger.info("mindtooth测试文件创建成功!");
            }
        } catch (IOException e) {
            logger.error("mindtooth测试文件创建失败: {}", e.getMessage());
        }

        try {
            Files.writeString(path, Arrays.toString(data) + System.lineSeparator(), StandardOpenOption.APPEND);
        } catch (IOException e) {
            logger.error("mindtooth测试文件写入失败: {}", e.getMessage());
        }
    }
}
