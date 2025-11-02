package com.hdu.neurostudent_signalflow.monitor;

import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Component;

import javax.imageio.ImageIO;
import java.awt.*;
import java.awt.image.BufferedImage;
import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.atomic.AtomicLong;

@Slf4j
public class ScreenMonitor {
    private static final int DEFAULT_TIME_INTERVAL = 500;   // 默认时间间隔，单位毫秒
    private static final long SHUTDOWN_TIMEOUT = 10;       // 关闭超时时间，单位秒

    // 使用原子类保证线程安全
    private static final AtomicInteger isRunning = new AtomicInteger(0); // 0-停止, 1-运行中
    private static final AtomicLong captureCount = new AtomicLong(0);    // 捕获次数统计
    private static final AtomicLong lastCaptureTime = new AtomicLong(0); // 最后捕获时间

    static {
        // 注册Shutdown Hook确保资源释放
        Runtime.getRuntime().addShutdownHook(new Thread(() -> {
            if (isRunning.get() == 1) {
                log.info("检测到JVM关闭，正在释放屏幕监控资源...");
                shutdown();
            }
        }));
    }

    // 监控异步单线程线程池
    private static final ScheduledExecutorService monitorExecutor =
            Executors.newSingleThreadScheduledExecutor(r -> {
                Thread thread = new Thread(r, "ScreenMonitor-Thread");
                thread.setDaemon(true); // 设置为守护线程
                thread.setUncaughtExceptionHandler((t, e) ->
                        log.error("ScreenMonitor线程发生未捕获异常: {}", e.getMessage(), e));
                return thread;
            });
    private static ScheduledFuture<?> monitorFuture;
    private static final CopyOnWriteArrayList<ScreenCaptureListener> listeners =
            new CopyOnWriteArrayList<>();

    // 私有构造器防止实例化
    private ScreenMonitor() {}

    /**
     * 开始屏幕监控
     * @return 是否成功启动
     */
    public static synchronized boolean startScreenMonitor() {
        return startScreenMonitor(DEFAULT_TIME_INTERVAL);
    }

    /**
     * 开始屏幕监控
     * @param timeInterval 捕获间隔（毫秒）
     * @return 是否成功启动
     */
    public static synchronized boolean startScreenMonitor(int timeInterval) {
        if (!isRunning.compareAndSet(0, 1)) {
            log.warn("屏幕监控已经在运行中");
            return false;
        }

        if (timeInterval < 100) {
            log.warn("捕获间隔过小({}ms)，已调整为最小值100ms", timeInterval);
            timeInterval = 100;
        }

        try {
            monitorFuture = monitorExecutor.scheduleWithFixedDelay(() -> {
                try {
                    byte[] imageData = captureFullScreenAsBytes();
                    captureCount.incrementAndGet();
                    lastCaptureTime.set(System.currentTimeMillis());

                    // 通知所有监听器
                    if (!listeners.isEmpty()) {
                        for (ScreenCaptureListener listener : listeners) {
                            try {
                                listener.onScreenCaptured(imageData);
                            } catch (Exception e) {
                                log.error("监听器处理截图时发生异常: {}", e.getMessage(), e);
                            }
                        }
                    }

                } catch (AWTException e) {
                    log.error("屏幕捕获AWT异常: {}", e.getMessage(), e);
                    // 如果是权限问题，可能需要停止监控
                    if (e.getMessage() != null && e.getMessage().contains("permission")) {
                        stopScreenMonitor();
                    }
                } catch (IOException e) {
                    log.error("屏幕捕获IO异常: {}", e.getMessage(), e);
                } catch (Exception e) {
                    log.error("屏幕捕获未知异常: {}", e.getMessage(), e);
                }
            }, 0, timeInterval, TimeUnit.MILLISECONDS);

            log.info("屏幕监控已启动，捕获间隔: {}ms", timeInterval);
            return true;

        } catch (Exception e) {
            isRunning.set(0);
            log.error("启动屏幕监控失败: {}", e.getMessage(), e);
            return false;
        }
    }

    /**
     * 停止屏幕监控
     * @return 是否成功停止
     */
    public static synchronized boolean stopScreenMonitor() {
        if (!isRunning.compareAndSet(1, 0)) {
            log.warn("屏幕监控未在运行");
            return false;
        }

        if (monitorFuture != null) {
            monitorFuture.cancel(false);
            monitorFuture = null;
        }

        log.info("屏幕监控已停止，总捕获次数: {}", captureCount.get());
        return true;
    }

    /**
     * 安全关闭所有资源
     */
    public static synchronized void shutdown() {
        stopScreenMonitor();

        if (!monitorExecutor.isShutdown()) {
            try {
                monitorExecutor.shutdown();
                if (!monitorExecutor.awaitTermination(SHUTDOWN_TIMEOUT, TimeUnit.SECONDS)) {
                    log.warn("线程池未及时终止，尝试强制关闭");
                    monitorExecutor.shutdownNow();
                }
                log.info("ScreenMonitor资源已释放");
            } catch (InterruptedException e) {
                monitorExecutor.shutdownNow();
                Thread.currentThread().interrupt();
                log.warn("关闭线程池时被中断");
            }
        }

        listeners.clear();
        captureCount.set(0);
        lastCaptureTime.set(0);
    }

    /**
     * 获取监控状态
     * @return 是否正在运行
     */
    public static boolean isRunning() {
        return isRunning.get() == 1;
    }

    /**
     * 获取监控统计信息
     * @return 监控统计信息
     */
    public static MonitorStats getMonitorStats() {
        return new MonitorStats(
                isRunning(),
                captureCount.get(),
                lastCaptureTime.get(),
                listeners.size()
        );
    }

    /**
     * 添加截图监听器
     * @param listener 监听器实例
     * @return 是否添加成功
     */
    public static boolean addScreenCaptureListener(ScreenCaptureListener listener) {
        if (listener != null && !listeners.contains(listener)) {
            listeners.add(listener);
            log.debug("添加截图监听器: {}", listener.getClass().getSimpleName());
            return true;
        }
        return false;
    }

    /**
     * 移除截图监听器
     * @param listener 监听器实例
     * @return 是否移除成功
     */
    public static boolean removeScreenCaptureListener(ScreenCaptureListener listener) {
        boolean removed = listeners.remove(listener);
        if (removed) {
            log.debug("移除截图监听器: {}", listener.getClass().getSimpleName());
        }
        return removed;
    }

    /**
     * 捕获全屏并返回BufferedImage对象
     * @return 屏幕画面的BufferedImage对象
     * @throws AWTException 如果平台配置不支持机器人功能
     */
    public static BufferedImage captureFullScreen() throws AWTException {
        // 检查图形环境
        if (GraphicsEnvironment.isHeadless()) {
            throw new AWTException("当前环境不支持图形操作（headless模式）");
        }

        Robot robot = new Robot();
        // 设置自动延迟，避免过快捕获
        robot.setAutoDelay(100);

        Rectangle screenRect = new Rectangle(Toolkit.getDefaultToolkit().getScreenSize());
        return robot.createScreenCapture(screenRect);
    }

    /**
     * 捕获全屏并返回字节数组（PNG格式）
     * @return PNG格式的字节数组
     * @throws AWTException 如果平台配置不支持机器人功能
     * @throws IOException 如果图像编码过程中发生I/O错误
     */
    public static byte[] captureFullScreenAsBytes() throws AWTException, IOException {
        BufferedImage image = captureFullScreen();
        try (ByteArrayOutputStream baos = new ByteArrayOutputStream()) {
            ImageIO.write(image, "png", baos);
            return baos.toByteArray();
        }
    }

    /**
     * 捕获全屏并保存为文件
     * @param filePath 文件路径
     * @return 是否保存成功
     */
    public static boolean captureFullScreenToFile(String filePath) {
        try {
            BufferedImage image = captureFullScreen();
            return ImageIO.write(image, "png", new java.io.File(filePath));
        } catch (Exception e) {
            log.error("保存截图到文件失败: {}", e.getMessage(), e);
            return false;
        }
    }

    /**
     * 截图监听器接口
     */
    public interface ScreenCaptureListener {
        /**
         * 截图完成回调
         * @param imageData PNG格式的图片字节数组
         */
        void onScreenCaptured(byte[] imageData);
    }

    /**
     * 监控统计信息
     */
    public static class MonitorStats {
        private final boolean running;
        private final long totalCaptures;
        private final long lastCaptureTime;
        private final int listenerCount;

        public MonitorStats(boolean running, long totalCaptures, long lastCaptureTime, int listenerCount) {
            this.running = running;
            this.totalCaptures = totalCaptures;
            this.lastCaptureTime = lastCaptureTime;
            this.listenerCount = listenerCount;
        }

        // Getter方法
        public boolean isRunning() { return running; }
        public long getTotalCaptures() { return totalCaptures; }
        public long getLastCaptureTime() { return lastCaptureTime; }
        public int getListenerCount() { return listenerCount; }

        @Override
        public String toString() {
            return String.format(
                    "MonitorStats{running=%s, totalCaptures=%d, lastCaptureTime=%d, listenerCount=%d}",
                    running, totalCaptures, lastCaptureTime, listenerCount
            );
        }
    }
}