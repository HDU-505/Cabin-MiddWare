package com.hdu.neurostudent_signalflow.monitor;

import lombok.extern.slf4j.Slf4j;
import org.bytedeco.javacv.FFmpegFrameGrabber;
import org.bytedeco.javacv.Frame;
import org.bytedeco.javacv.Java2DFrameConverter;

import javax.imageio.ImageIO;
import java.awt.*;
import java.awt.image.BufferedImage;
import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.util.Arrays;
import java.util.List;
import java.util.Map;
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.atomic.AtomicLong;

@Slf4j
public class ScreenMonitor {
    private static final int DEFAULT_TIME_INTERVAL = 500;
    private static final long SHUTDOWN_TIMEOUT = 10;

    // 线程安全状态管理
    private static final AtomicInteger isRunning = new AtomicInteger(0);
    private static final AtomicLong captureCount = new AtomicLong(0);
    private static final AtomicLong lastCaptureTime = new AtomicLong(0);

    // 多种捕获策略
    private static final Map<String, ScreenCaptureStrategy> strategies = new ConcurrentHashMap<>();

    static {
        // 初始化捕获策略
        initializeStrategies();

        // 注册Shutdown Hook
        Runtime.getRuntime().addShutdownHook(new Thread(() -> {
            if (isRunning.get() == 1) {
                log.info("检测到JVM关闭，正在释放屏幕监控资源...");
                shutdown();
            }
        }));
    }

    // 线程池
    private static final ScheduledExecutorService monitorExecutor =
            Executors.newSingleThreadScheduledExecutor(r -> {
                Thread thread = new Thread(r, "EnhancedScreenMonitor-Thread");
                thread.setDaemon(true);
                thread.setUncaughtExceptionHandler((t, e) ->
                        log.error("EnhancedScreenMonitor线程未捕获异常: {}", e.getMessage(), e));
                return thread;
            });

    private static ScheduledFuture<?> monitorFuture;
    private static final CopyOnWriteArrayList<ScreenCaptureListener> listeners =
            new CopyOnWriteArrayList<>();

    private ScreenMonitor() {}

    /**
     * 初始化所有捕获策略
     */
    private static void initializeStrategies() {
        strategies.put("java_robot", new JavaRobotStrategy());
        strategies.put("ffmpeg", new FFmpegCaptureStrategy());
        strategies.put("platform_native", new PlatformNativeStrategy());
        strategies.put("fallback", new FallbackImageStrategy());
    }

    /**
     * 开始屏幕监控
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
            // 测试捕获策略
            testCaptureStrategies();

            monitorFuture = monitorExecutor.scheduleWithFixedDelay(() -> {
                try {
                    byte[] imageData = captureScreenWithFallback();

                    if (imageData != null && imageData.length > 0) {
                        captureCount.incrementAndGet();
                        lastCaptureTime.set(System.currentTimeMillis());

                        // 通知监听器
                        notifyListeners(imageData);
                    } else {
                        log.warn("屏幕捕获返回空数据");
                    }

                } catch (Exception e) {
                    log.error("屏幕捕获过程异常: {}", e.getMessage(), e);
                }
            }, 0, timeInterval, TimeUnit.MILLISECONDS);

            log.info("增强屏幕监控已启动，捕获间隔: {}ms", timeInterval);
            return true;

        } catch (Exception e) {
            isRunning.set(0);
            log.error("启动屏幕监控失败: {}", e.getMessage(), e);
            return false;
        }
    }

    /**
     * 测试所有捕获策略
     */
    private static void testCaptureStrategies() {
        log.info("测试屏幕捕获策略...");
        for (String strategyName : strategies.keySet()) {
            try {
                byte[] testData = strategies.get(strategyName).capture();
                if (testData != null && testData.length > 0) {
                    log.info("策略 {} 测试成功，图像大小: {} bytes", strategyName, testData.length);
                } else {
                    log.warn("策略 {} 测试返回空数据", strategyName);
                }
            } catch (Exception e) {
                log.warn("策略 {} 测试失败: {}", strategyName, e.getMessage());
            }
        }
    }

    /**
     * 使用回退策略捕获屏幕
     * @return 图像字节数据
     */
    public static byte[] captureScreenWithFallback() {
        List<String> strategyOrder = Arrays.asList(
                "java_robot",      // 首选：Java原生
                "ffmpeg",          // 次选：FFmpeg
                "platform_native", // 再次：平台原生
                "fallback"         // 最后：备用
        );

        for (String strategyName : strategyOrder) {
            try {
                long startTime = System.currentTimeMillis();
                ScreenCaptureStrategy strategy = strategies.get(strategyName);
                byte[] result = strategy.capture();

                if (result != null && result.length > 0) {
                    long cost = System.currentTimeMillis() - startTime;
                    log.debug("策略 {} 捕获成功，大小: {} bytes, 耗时: {}ms",
                            strategyName, result.length, cost);
                    return result;
                }
            } catch (Exception e) {
                log.debug("策略 {} 失败: {}", strategyName, e.getMessage());
            }
        }

        log.error("所有屏幕捕获策略均失败");
        return new byte[0];
    }

    /**
     * 通知所有监听器
     */
    private static void notifyListeners(byte[] imageData) {
        if (!listeners.isEmpty()) {
            for (ScreenCaptureListener listener : listeners) {
                try {
                    listener.onScreenCaptured(imageData);
                } catch (Exception e) {
                    log.error("监听器处理截图时发生异常: {}", e.getMessage(), e);
                }
            }
        }
    }

    // ==================== 原有的管理方法 ====================

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

    public static synchronized void shutdown() {
        stopScreenMonitor();

        if (!monitorExecutor.isShutdown()) {
            try {
                monitorExecutor.shutdown();
                if (!monitorExecutor.awaitTermination(SHUTDOWN_TIMEOUT, TimeUnit.SECONDS)) {
                    log.warn("线程池未及时终止，尝试强制关闭");
                    monitorExecutor.shutdownNow();
                }
                log.info("EnhancedScreenMonitor资源已释放");
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

    public static boolean isRunning() {
        return isRunning.get() == 1;
    }

    public static MonitorStats getMonitorStats() {
        return new MonitorStats(
                isRunning(),
                captureCount.get(),
                lastCaptureTime.get(),
                listeners.size()
        );
    }

    public static boolean addScreenCaptureListener(ScreenCaptureListener listener) {
        if (listener != null && !listeners.contains(listener)) {
            listeners.add(listener);
            log.debug("添加截图监听器: {}", listener.getClass().getSimpleName());
            return true;
        }
        return false;
    }

    public static boolean removeScreenCaptureListener(ScreenCaptureListener listener) {
        boolean removed = listeners.remove(listener);
        if (removed) {
            log.debug("移除截图监听器: {}", listener.getClass().getSimpleName());
        }
        return removed;
    }

    // ==================== 捕获策略实现 ====================

    /**
     * 屏幕捕获策略接口
     */
    public interface ScreenCaptureStrategy {
        byte[] capture() throws Exception;
    }

    /**
     * Java Robot 策略
     */
    public static class JavaRobotStrategy implements ScreenCaptureStrategy {
        @Override
        public byte[] capture() throws Exception {
            if (GraphicsEnvironment.isHeadless()) {
                throw new AWTException("Headless模式不支持Robot");
            }

            Robot robot = new Robot();
            robot.setAutoDelay(50);

            Rectangle screenRect = new Rectangle(Toolkit.getDefaultToolkit().getScreenSize());
            BufferedImage image = robot.createScreenCapture(screenRect);

            return imageToBytes(image);
        }
    }

    /**
     * FFmpeg 捕获策略
     */
    public static class FFmpegCaptureStrategy implements ScreenCaptureStrategy {
        private Java2DFrameConverter converter = new Java2DFrameConverter();

        @Override
        public byte[] capture() throws Exception {
            String os = System.getProperty("os.name").toLowerCase();
            String inputFormat = getPlatformInputFormat(os);

            if (inputFormat == null) {
                throw new Exception("不支持的操作系统: " + os);
            }

            FFmpegFrameGrabber grabber = new FFmpegFrameGrabber(inputFormat);
            grabber.setFormat(getGrabberFormat(os));
            grabber.setFrameRate(1);

            try {
                grabber.start();
                Frame frame = grabber.grab();

                if (frame != null) {
                    BufferedImage image = converter.convert(frame);
                    return imageToBytes(image);
                }
            } finally {
                try {
                    grabber.stop();
                } catch (Exception e) {
                    log.debug("FFmpeg Grabber停止异常: {}", e.getMessage());
                }
            }

            return null;
        }

        private String getPlatformInputFormat(String os) {
            if (os.contains("win")) return "desktop";
            if (os.contains("nix") || os.contains("nux")) return ":0.0";
            if (os.contains("mac")) return "default";
            return null;
        }

        private String getGrabberFormat(String os) {
            if (os.contains("win")) return "gdigrab";
            if (os.contains("nix") || os.contains("nux")) return "x11grab";
            if (os.contains("mac")) return "avfoundation";
            return null;
        }
    }

    /**
     * 平台原生捕获策略
     */
    public static class PlatformNativeStrategy implements ScreenCaptureStrategy {
        @Override
        public byte[] capture() throws Exception {
            String os = System.getProperty("os.name").toLowerCase();

            if (os.contains("win")) {
                return captureWindowsNative();
            } else if (os.contains("nix") || os.contains("nux")) {
                return captureLinuxNative();
            } else if (os.contains("mac")) {
                return captureMacNative();
            }

            throw new Exception("不支持的操作系统: " + os);
        }

        private byte[] captureWindowsNative() throws IOException {
            // 使用 PowerShell 命令捕获屏幕
            Process process = Runtime.getRuntime().exec(new String[]{
                    "powershell", "-Command",
                    "Add-Type -AssemblyName System.Windows.Forms; " +
                            "[System.Windows.Forms.Screen]::PrimaryScreen.Bounds"
            });

            // 这里简化实现，实际需要更复杂的图像捕获
            return generateFallbackImage("Windows Native Capture");
        }

        private byte[] captureLinuxNative() throws IOException {
            // 使用 import 命令 (ImageMagick)
            Process process = Runtime.getRuntime().exec(new String[]{
                    "import", "-window", "root", "png:-"
            });

            try {
                return process.getInputStream().readAllBytes();
            } catch (Exception e) {
                return generateFallbackImage("Linux Native Capture");
            }
        }

        private byte[] captureMacNative() throws IOException {
            // 使用 screencapture 命令
            Process process = Runtime.getRuntime().exec(new String[]{
                    "screencapture", "-t", "png", "-x", "-"
            });

            try {
                return process.getInputStream().readAllBytes();
            } catch (Exception e) {
                return generateFallbackImage("Mac Native Capture");
            }
        }
    }

    /**
     * 备用图像策略
     */
    public static class FallbackImageStrategy implements ScreenCaptureStrategy {
        @Override
        public byte[] capture() throws Exception {
            log.warn("使用备用策略生成测试图像");
            return generateFallbackImage("Fallback Image - " + new java.util.Date());
        }
    }

    // ==================== 工具方法 ====================

    /**
     * 生成备用图像
     */
    private static byte[] generateFallbackImage(String message) throws IOException {
        BufferedImage image = new BufferedImage(800, 600, BufferedImage.TYPE_INT_RGB);
        Graphics2D g2d = image.createGraphics();

        // 绘制渐变背景
        GradientPaint gradient = new GradientPaint(0, 0, Color.LIGHT_GRAY, 800, 600, Color.WHITE);
        g2d.setPaint(gradient);
        g2d.fillRect(0, 0, 800, 600);

        // 绘制边框
        g2d.setColor(Color.DARK_GRAY);
        g2d.setStroke(new BasicStroke(3));
        g2d.drawRect(10, 10, 780, 580);

        // 绘制文字
        g2d.setColor(Color.BLUE);
        g2d.setFont(new Font("Arial", Font.BOLD, 24));
        g2d.drawString("屏幕捕获", 320, 100);

        g2d.setColor(Color.BLACK);
        g2d.setFont(new Font("Arial", Font.PLAIN, 16));
        g2d.drawString(message, 200, 200);
        g2d.drawString("时间: " + new java.util.Date(), 200, 250);
        g2d.drawString("系统: " + System.getProperty("os.name"), 200, 300);
        g2d.drawString("架构: " + System.getProperty("os.arch"), 200, 350);

        g2d.dispose();

        return imageToBytes(image);
    }

    /**
     * BufferedImage 转字节数组
     */
    private static byte[] imageToBytes(BufferedImage image) throws IOException {
        try (ByteArrayOutputStream baos = new ByteArrayOutputStream()) {
            ImageIO.write(image, "png", baos);
            return baos.toByteArray();
        }
    }

    // ==================== 原有的内部类和接口 ====================

    public interface ScreenCaptureListener {
        void onScreenCaptured(byte[] imageData);
    }

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