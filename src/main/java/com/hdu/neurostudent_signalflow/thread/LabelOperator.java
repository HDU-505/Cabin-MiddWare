package com.hdu.neurostudent_signalflow.thread;

import com.alibaba.fastjson.JSON;
import com.hdu.neurostudent_signalflow.entity.UnifyData;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.BlockingQueue;

public class LabelOperator implements Runnable {
    private static final Logger logger = LoggerFactory.getLogger(LabelOperator.class);

    private final BlockingQueue<double[]> revData;
    private final BlockingQueue<String> sendQueue;
    private volatile boolean running = true;

    public LabelOperator(BlockingQueue<double[]> revData, BlockingQueue<String> sendQueue) {
        this.revData = revData;
        this.sendQueue = sendQueue;
    }

    @Override
    public void run() {
        while (running) {
            try {
                double[] dataArr = revData.take(); // 阻塞等待数据
                if (dataArr == null || dataArr.length != 2) {
                    logger.warn("Invalid data received: {}", dataArr);
                    continue;
                }

                // 构建 UnifyData
                UnifyData unifyData = new UnifyData("paradigm", "v1.0", "20", "1", "label");
                unifyData.setTimeStamp(String.format("%.0f", dataArr[0]));

                List<Double> data = new ArrayList<>();
                data.add(dataArr[1]);
                unifyData.data = data;

                // 转换成 JSON
                String labelJson = JSON.toJSONString(unifyData);

                // 放入发送队列
                sendQueue.put(labelJson);
            } catch (InterruptedException e) {
                logger.info("LabelOperator interrupted, stopping thread.");
                Thread.currentThread().interrupt(); // 保留中断状态
                break;
            } catch (Exception e) {
                logger.error("Error processing label data", e);
            }
        }
    }

    // 停止线程
    public void stop() {
        running = false;
        Thread.currentThread().interrupt();
    }
}
