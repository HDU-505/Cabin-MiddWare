package com.hdu.neurostudent_signalflow.monitor;

import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.awt.*;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class ScreenMonitorTest {

    @Mock
    private ScreenMonitor.ScreenCaptureListener mockListener;

    @BeforeEach
    void setUp() {
        // 只确保监控是停止状态，不关闭线程池
        ScreenMonitor.stopScreenMonitor();
        // 清理之前的监听器
        ScreenMonitor.removeScreenCaptureListener(mockListener);
    }

    @AfterEach
    void tearDown() {
        // 只停止监控，不关闭线程池，保持线程池可用
        ScreenMonitor.stopScreenMonitor();
        // 清理测试中添加的监听器
        ScreenMonitor.removeScreenCaptureListener(mockListener);
    }

    @AfterAll
    static void afterAll() {
        // 在所有测试完成后才关闭线程池，释放资源
        ScreenMonitor.shutdown();
    }

    @Test
    void testStartAndStop() {
        // 测试启动
        assertTrue(ScreenMonitor.startScreenMonitor());
        assertTrue(ScreenMonitor.isRunning());

        // 测试重复启动
        assertFalse(ScreenMonitor.startScreenMonitor());

        // 测试停止
        assertTrue(ScreenMonitor.stopScreenMonitor());
        assertFalse(ScreenMonitor.isRunning());

        // 测试重复停止
        assertFalse(ScreenMonitor.stopScreenMonitor());
    }

    @Test
    void testStartWithCustomInterval() {
        // 测试过小的间隔会被调整
        assertTrue(ScreenMonitor.startScreenMonitor(50));
        assertTrue(ScreenMonitor.isRunning());
        assertTrue(ScreenMonitor.stopScreenMonitor());

        // 测试正常间隔
        assertTrue(ScreenMonitor.startScreenMonitor(1000));
        assertTrue(ScreenMonitor.isRunning());
        assertTrue(ScreenMonitor.stopScreenMonitor());
    }

    @Test
    void testListenerManagement() {
        // 测试添加监听器
        assertTrue(ScreenMonitor.addScreenCaptureListener(mockListener));

        // 测试重复添加同一监听器
        assertFalse(ScreenMonitor.addScreenCaptureListener(mockListener));

        // 测试移除监听器
        assertTrue(ScreenMonitor.removeScreenCaptureListener(mockListener));

        // 测试移除不存在的监听器
        assertFalse(ScreenMonitor.removeScreenCaptureListener(mockListener));
    }

    @Test
    void testScreenCaptureFunctionality() {
        // 测试截图功能（在有图形环境的情况下）
        if (!GraphicsEnvironment.isHeadless()) {
            // 测试捕获为 BufferedImage
            assertDoesNotThrow(() -> {
                Image image = ScreenMonitor.captureFullScreen();
                assertNotNull(image);
                assertTrue(image.getWidth(null) > 0);
                assertTrue(image.getHeight(null) > 0);
            });

            // 测试捕获为字节数组
            assertDoesNotThrow(() -> {
                byte[] imageData = ScreenMonitor.captureFullScreenAsBytes();
                assertNotNull(imageData);
                assertTrue(imageData.length > 0);
            });

            // 测试保存到文件
            String testFilePath = "test_screenshot.png";
            boolean saved = ScreenMonitor.captureFullScreenToFile(testFilePath);

            // 如果保存成功，清理测试文件
            if (saved) {
                java.io.File testFile = new java.io.File(testFilePath);
                if (testFile.exists()) {
                    assertTrue(testFile.delete());
                }
            }
        } else {
            System.out.println("运行在无头环境中，跳过图形功能测试");
        }
    }

    @Test
    void testMonitorWithListener() throws InterruptedException {
        // 设置测试监听器
        AtomicInteger captureCount = new AtomicInteger(0);
        CountDownLatch latch = new CountDownLatch(1);

        ScreenMonitor.ScreenCaptureListener testListener = imageData -> {
            captureCount.incrementAndGet();
            assertNotNull(imageData);
            assertTrue(imageData.length > 0);
            latch.countDown();
        };

        // 添加监听器并启动监控
        ScreenMonitor.addScreenCaptureListener(testListener);
        assertTrue(ScreenMonitor.startScreenMonitor(100)); // 使用较短的间隔

        // 等待捕获完成
        boolean captured = latch.await(3, TimeUnit.SECONDS);

        // 验证
        assertTrue(captured, "截图应该在3秒内完成");
        assertTrue(captureCount.get() >= 1, "至少应该捕获一次");

        // 清理（会在 @AfterEach 中处理）
    }

    @Test
    void testMonitorStats() throws InterruptedException {
        // 启动前检查状态
        ScreenMonitor.MonitorStats statsBefore = ScreenMonitor.getMonitorStats();
        assertFalse(statsBefore.isRunning());
        assertEquals(0, statsBefore.getTotalCaptures());

        // 启动监控
        assertTrue(ScreenMonitor.startScreenMonitor(100));

        // 等待一段时间让监控运行
        Thread.sleep(200);

        // 检查运行中状态
        ScreenMonitor.MonitorStats statsDuring = ScreenMonitor.getMonitorStats();
        assertTrue(statsDuring.isRunning());
        assertTrue(statsDuring.getTotalCaptures() > 0);
        assertTrue(statsDuring.getLastCaptureTime() > 0);

        // 停止监控
        assertTrue(ScreenMonitor.stopScreenMonitor());

        // 检查停止后状态
        ScreenMonitor.MonitorStats statsAfter = ScreenMonitor.getMonitorStats();
        assertFalse(statsAfter.isRunning());
        assertTrue(statsAfter.getTotalCaptures() > 0);
    }

    @Test
    void testListenerExceptionHandling() throws InterruptedException {
        // 创建会抛出异常的监听器
        ScreenMonitor.ScreenCaptureListener failingListener = imageData -> {
            throw new RuntimeException("测试异常");
        };

        // 添加正常监听器和异常监听器
        CountDownLatch latch = new CountDownLatch(1);
        ScreenMonitor.ScreenCaptureListener normalListener = imageData -> {
            assertNotNull(imageData);
            latch.countDown();
        };

        ScreenMonitor.addScreenCaptureListener(failingListener);
        ScreenMonitor.addScreenCaptureListener(normalListener);

        // 启动监控 - 异常不应该影响其他监听器
        assertTrue(ScreenMonitor.startScreenMonitor(100));

        // 等待正常监听器执行
        boolean completed = latch.await(3, TimeUnit.SECONDS);

        // 验证正常监听器仍然工作
        assertTrue(completed, "即使有监听器异常，其他监听器也应该正常工作");

        // 清理
        ScreenMonitor.removeScreenCaptureListener(failingListener);
        ScreenMonitor.removeScreenCaptureListener(normalListener);
    }


    @Test
    void testMultipleStartStopCycles() {
        // 测试多次启动停止循环
        for (int i = 0; i < 3; i++) {
            assertTrue(ScreenMonitor.startScreenMonitor(200));
            assertTrue(ScreenMonitor.isRunning());

            // 短暂运行
            assertDoesNotThrow(() -> Thread.sleep(50));

            assertTrue(ScreenMonitor.stopScreenMonitor());
            assertFalse(ScreenMonitor.isRunning());
        }
    }

    @Test
    void testConcurrentAccess() throws InterruptedException {
        int threadCount = 5;
        CountDownLatch startLatch = new CountDownLatch(1);
        CountDownLatch endLatch = new CountDownLatch(threadCount);
        AtomicInteger successCount = new AtomicInteger(0);

        // 创建多个线程同时访问
        for (int i = 0; i < threadCount; i++) {
            new Thread(() -> {
                try {
                    startLatch.await();
                    if (ScreenMonitor.startScreenMonitor()) {
                        successCount.incrementAndGet();
                    }
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                } finally {
                    endLatch.countDown();
                }
            }).start();
        }

        // 同时启动所有线程
        startLatch.countDown();
        boolean allThreadsCompleted = endLatch.await(3, TimeUnit.SECONDS);

        // 验证只有一个线程成功启动
        assertTrue(allThreadsCompleted, "所有线程应该在3秒内完成");
        assertEquals(1, successCount.get(), "应该只有一个线程成功启动监控");
        assertTrue(ScreenMonitor.isRunning(), "监控应该在运行状态");

        // 清理
        ScreenMonitor.stopScreenMonitor();
    }

}