package com.hdu.neurostudent_signalflow.adapter;

import com.hdu.neurostudent_signalflow.thread.MindToothOperator;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.mockito.Mockito;

import java.util.concurrent.BlockingDeque;
import java.util.concurrent.LinkedBlockingDeque;
import java.util.concurrent.TimeUnit;

import static org.mockito.Mockito.*;

class MindToothDeviceAdapterTest {

    private MindToothDeviceAdapter adapter;
    private MindToothOperator operator;   // mock依赖
    private BlockingDeque<double[]> inputQueue;

    @BeforeEach
    void setUp() {
        // 1. mock 依赖
        operator = mock(MindToothOperator.class);

        // 2. 手动 new Adapter，不走 Spring
        adapter = new MindToothDeviceAdapter();
        adapter.init();

        // 3. 手动注入依赖
//        adapter.mindToothOperator = operator;

        // 4. 初始化队列
        inputQueue = new LinkedBlockingDeque<>();
        adapter.addData(inputQueue);
    }

    @Test
    void testProcessDevice_DistributesData() throws Exception {
        // 启动处理线程
        adapter.processDevice();

        // 模拟放入数据
        double[] sample1 = {1.0, 2.0};
        double[] sample2 = {3.0, 4.0};
        inputQueue.put(sample1);
        inputQueue.put(sample2);

        // 等待线程消费
        TimeUnit.SECONDS.sleep(2);

        // 验证 operator 被调用
        verify(operator, atLeastOnce()).EEGData2UnifyData(sample1);
        verify(operator, atLeastOnce()).EEGData2UnifyData(sample2);
    }
}
