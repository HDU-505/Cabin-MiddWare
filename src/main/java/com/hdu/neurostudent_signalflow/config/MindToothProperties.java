package com.hdu.neurostudent_signalflow.config;

import lombok.Data;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.stereotype.Component;

@Component
@ConfigurationProperties("mindtooth")
@Data
public class MindToothProperties {
    private String impedance_name;    //MindTooth的LSL流出口名（阻抗值）
    private String data_name;    //MindTooth的LSL流出口名（数据）

    private double impedance_id;   //MindTooth阻抗值的类别，默认为0
    private double data_id;   //MindTooth数据的类别，默认为1

    private String sampeRate;   //设备的采样率
    private String dataChannels;    //设备的数据通道数
    private String impChannels;    //设备的阻抗通道数
    private double impedance_or_data;   //用于表示当前SDK传的数据是阻抗值还是数据,1表示数据，0表示阻抗

    private boolean enabled;  //是否启用mindtooth

    // mindtooth 程序相关配置
    private String python_path;
    private String sdk_path;
    private int max_retry_count;

    // 适配器相关配置
    private int processThread;

    // 测试相关配置
    private boolean testEnable;
    private String testInputFile;
    private String testOutputFile;
}
