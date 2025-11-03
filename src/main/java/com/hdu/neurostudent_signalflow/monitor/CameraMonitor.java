package com.hdu.neurostudent_signalflow.monitor;

import com.github.sarxos.webcam.Webcam;
import com.github.sarxos.webcam.WebcamResolution;
import lombok.extern.slf4j.Slf4j;

import javax.imageio.ImageIO;
import java.awt.*;
import java.awt.image.BufferedImage;
import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.atomic.AtomicLong;

@Slf4j
public class CameraMonitor extends BaseMonitor {
    private static final int DEFAULT_TIME_INTERVAL = 1000;
    private static final long SHUTDOWN_TIMEOUT = 10;
    private static final String TYPE = "camera";
    private static final int DEFAULT_IMAGE_WIDTH = 1280;
    private static final int DEFAULT_IMAGE_HEIGHT = 720;

    // 线程安全控制
    private static final AtomicInteger isRunning = new AtomicInteger(0);
    private static final AtomicLong captureCount = new AtomicLong(0);
    private static final AtomicLong lastCaptureTime = new AtomicLong(0);
    private static final AtomicLong errorImageCount = new AtomicLong(0);

    // 摄像头相关
    private static Webcam webcam;
    private static volatile boolean cameraInitialized = false;
    private static volatile boolean useFallbackImage = false;

    // 线程池
    private static final ScheduledExecutorService monitorExecutor =
            Executors.newSingleThreadScheduledExecutor(r -> {
                Thread thread = new Thread(r, "CameraMonitor-Thread");
                thread.setDaemon(true);
                thread.setUncaughtExceptionHandler((t, e) ->
                        log.error("CameraMonitor线程异常: {}", e.getMessage(), e));
                return thread;
            });
    private static ScheduledFuture<?> monitorFuture;
    private static final CopyOnWriteArrayList<MonitorCaptureListener> listeners =
            new CopyOnWriteArrayList<>();

    static {
        Runtime.getRuntime().addShutdownHook(new Thread(() -> {
            if (isRunning.get() == 1) {
                log.info("JVM关闭，释放摄像头资源...");
                shutdown();
            }
        }));
    }

    /**
     * 生成默认错误图像
     */
    private static byte[] generateDefaultImage(String title, String message) {
        try {
            BufferedImage image = new BufferedImage(DEFAULT_IMAGE_WIDTH, DEFAULT_IMAGE_HEIGHT, BufferedImage.TYPE_INT_RGB);
            Graphics2D g2d = image.createGraphics();

            // 设置背景和文字
            g2d.setColor(Color.WHITE);
            g2d.fillRect(0, 0, DEFAULT_IMAGE_WIDTH, DEFAULT_IMAGE_HEIGHT);
            g2d.setColor(Color.BLACK);

            // 标题
            g2d.setFont(new Font("Microsoft YaHei", Font.BOLD, 36));
            FontMetrics metrics = g2d.getFontMetrics();
            int titleWidth = metrics.stringWidth(title);
            int titleX = (DEFAULT_IMAGE_WIDTH - titleWidth) / 2;
            int titleY = DEFAULT_IMAGE_HEIGHT / 2 - 20;
            g2d.drawString(title, titleX, titleY);

            // 消息
            g2d.setFont(new Font("Microsoft YaHei", Font.PLAIN, 24));
            metrics = g2d.getFontMetrics();
            int msgWidth = metrics.stringWidth(message);
            int msgX = (DEFAULT_IMAGE_WIDTH - msgWidth) / 2;
            int msgY = DEFAULT_IMAGE_HEIGHT / 2 + 40;
            g2d.drawString(message, msgX, msgY);

            g2d.dispose();

            // 转换为字节数组
            try (ByteArrayOutputStream baos = new ByteArrayOutputStream()) {
                ImageIO.write(image, "png", baos);
                errorImageCount.incrementAndGet();
                return baos.toByteArray();
            }
        } catch (Exception e) {
            log.error("生成默认图像失败: {}", e.getMessage());
            return new byte[0];
        }
    }

    /**
     * 初始化摄像头
     */
    public static synchronized boolean initializeCamera() {
        if (cameraInitialized) {
            log.warn("摄像头已经初始化，先释放当前摄像头");
            releaseCamera();
        }

        try {
            // 获取默认摄像头
            webcam = Webcam.getDefault();

            if (webcam == null) {
                log.error("未找到可用的摄像头");
                return false;
            }

            // 设置分辨率
            Dimension[] resolutions = webcam.getViewSizes();
            Dimension targetResolution = new Dimension(DEFAULT_IMAGE_WIDTH, DEFAULT_IMAGE_HEIGHT);

            // 寻找最接近的分辨率
            Dimension bestResolution = null;
            for (Dimension res : resolutions) {
                if (bestResolution == null ||
                        Math.abs(res.width - DEFAULT_IMAGE_WIDTH) < Math.abs(bestResolution.width - DEFAULT_IMAGE_WIDTH)) {
                    bestResolution = res;
                }
            }

            if (bestResolution != null) {
                webcam.setViewSize(bestResolution);
                log.info("设置摄像头分辨率: {}x{}", bestResolution.width, bestResolution.height);
            } else {
                webcam.setViewSize(WebcamResolution.VGA.getSize());
                log.info("使用默认VGA分辨率");
            }

            // 打开摄像头
            webcam.open();
            cameraInitialized = true;
            useFallbackImage = false;

            log.info("摄像头初始化成功");
            return true;

        } catch (Exception e) {
            log.error("摄像头初始化异常: {}", e.getMessage(), e);
            releaseCamera();
            return false;
        }
    }

    /**
     * 检测可用摄像头
     */
    public static List<Webcam> detectAvailableCameras() {
        List<Webcam> availableCameras = new ArrayList<>();
        try {
            List<Webcam> webcams = Webcam.getWebcams();
            for (Webcam cam : webcams) {
                try {
                    cam.open();
                    if (cam.isOpen()) {
                        availableCameras.add(cam);
                        Dimension size = cam.getViewSize();
                        log.info("检测到摄像头: {}, 分辨率: {}x{}",
                                cam.getName(), size.width, size.height);
                    }
                    cam.close();
                } catch (Exception e) {
                    log.debug("检测摄像头失败: {}", e.getMessage());
                }
            }
        } catch (Exception e) {
            log.error("检测摄像头异常: {}", e.getMessage());
        }

        log.info("共检测到 {} 个可用摄像头", availableCameras.size());
        return availableCameras;
    }

    /**
     * 开始摄像头监控
     */
    public static synchronized boolean startCameraMonitor() {
        return startCameraMonitor(DEFAULT_TIME_INTERVAL);
    }

    /**
     * 开始摄像头监控
     */
    public static synchronized boolean startCameraMonitor(int timeInterval) {
        if (!isRunning.compareAndSet(0, 1)) {
            log.warn("摄像头监控已经在运行中");
            return false;
        }

        if (timeInterval < 100) {
            log.warn("捕获间隔过小({}ms)，调整为100ms", timeInterval);
            timeInterval = 100;
        }

        // 初始化摄像头
        if (!cameraInitialized && !initializeCamera()) {
            log.warn("摄像头初始化失败，使用默认图像模式");
            useFallbackImage = true;
        }

        try {
            monitorFuture = monitorExecutor.scheduleWithFixedDelay(() -> {
                try {
                    byte[] imageData = captureFrameAsBytes();
                    if (imageData != null && imageData.length > 0) {
                        captureCount.incrementAndGet();
                        lastCaptureTime.set(System.currentTimeMillis());

                        // 通知监听器
                        if (!listeners.isEmpty()) {
                            for (MonitorCaptureListener listener : listeners) {
                                try {
                                    listener.onCaptured(TYPE, imageData);
                                } catch (Exception e) {
                                    log.error("监听器处理异常: {}", e.getMessage(), e);
                                }
                            }
                        }
                    }
                } catch (Exception e) {
                    log.error("捕获异常: {}", e.getMessage());
                    useFallbackImage = true;
                }
            }, 0, timeInterval, TimeUnit.MILLISECONDS);

            String mode = useFallbackImage ? "默认图像模式" : "正常摄像头模式";
            log.info("摄像头监控已启动，模式: {}, 捕获间隔: {}ms", mode, timeInterval);
            return true;

        } catch (Exception e) {
            isRunning.set(0);
            log.error("启动摄像头监控失败: {}", e.getMessage(), e);
            return false;
        }
    }

    /**
     * 捕获帧为字节数组
     */
    public static byte[] captureFrameAsBytes() {
        if (useFallbackImage || !cameraInitialized || webcam == null) {
            if (!cameraInitialized) {
                return generateDefaultImage("摄像头不可用", "未检测到可用摄像头");
            } else {
                return generateDefaultImage("摄像头异常", "图像捕获失败");
            }
        }

        try {
            BufferedImage image = webcam.getImage();
            if (image == null) {
                log.warn("摄像头返回空图像");
                return generateDefaultImage("图像捕获失败", "摄像头返回空数据");
            }

            try (ByteArrayOutputStream baos = new ByteArrayOutputStream()) {
                ImageIO.write(image, "png", baos);
                return baos.toByteArray();
            }
        } catch (Exception e) {
            log.error("捕获图像异常: {}", e.getMessage());
            return generateDefaultImage("系统异常", "捕获过程中发生错误");
        }
    }

    /**
     * 捕获帧为BufferedImage
     */
    public static BufferedImage captureFrame() {
        try {
            byte[] imageData = captureFrameAsBytes();
            if (imageData != null && imageData.length > 0) {
                return ImageIO.read(new ByteArrayInputStream(imageData));
            }
        } catch (Exception e) {
            log.error("捕获帧失败: {}", e.getMessage());
        }
        return null;
    }

    /**
     * 停止摄像头监控
     */
    public static synchronized boolean stopCameraMonitor() {
        if (!isRunning.compareAndSet(1, 0)) {
            log.warn("摄像头监控未在运行");
            return false;
        }

        if (monitorFuture != null) {
            monitorFuture.cancel(false);
            monitorFuture = null;
        }

        log.info("摄像头监控已停止，总捕获次数: {}", captureCount.get());
        return true;
    }

    /**
     * 释放摄像头资源
     */
    private static synchronized void releaseCamera() {
        if (webcam != null) {
            try {
                webcam.close();
                webcam = null;
                cameraInitialized = false;
                log.info("摄像头资源已释放");
            } catch (Exception e) {
                log.error("释放摄像头资源异常: {}", e.getMessage(), e);
            }
        }
    }

    /**
     * 安全关闭
     */
    public static synchronized void shutdown() {
        stopCameraMonitor();
        releaseCamera();

        if (!monitorExecutor.isShutdown()) {
            try {
                monitorExecutor.shutdown();
                if (!monitorExecutor.awaitTermination(SHUTDOWN_TIMEOUT, TimeUnit.SECONDS)) {
                    monitorExecutor.shutdownNow();
                }
                log.info("CameraMonitor资源已释放");
            } catch (InterruptedException e) {
                monitorExecutor.shutdownNow();
                Thread.currentThread().interrupt();
            }
        }

        listeners.clear();
        captureCount.set(0);
        lastCaptureTime.set(0);
        errorImageCount.set(0);
    }

    // 状态获取方法
    public static boolean isRunning() { return isRunning.get() == 1; }
    public static boolean isCameraInitialized() { return cameraInitialized; }
    public static boolean isUsingFallbackImage() { return useFallbackImage; }

    /**
     * 设置是否使用默认图像
     */
    public static void setUseFallbackImage(boolean useFallback) {
        useFallbackImage = useFallback;
        log.info("已{}默认图像模式", useFallback ? "启用" : "禁用");
    }

    /**
     * 添加监听器
     */
    public static boolean addCameraCaptureListener(MonitorCaptureListener listener) {
        if (listener != null && !listeners.contains(listener)) {
            listeners.add(listener);
            log.debug("添加摄像头捕获监听器: {}", listener.getClass().getSimpleName());
            return true;
        }
        return false;
    }

    /**
     * 移除监听器
     */
    public static boolean removeCameraCaptureListener(MonitorCaptureListener listener) {
        boolean removed = listeners.remove(listener);
        if (removed) {
            log.debug("移除摄像头捕获监听器: {}", listener.getClass().getSimpleName());
        }
        return removed;
    }

    /**
     * 保存帧到文件
     */
    public static boolean captureFrameToFile(String filePath) {
        try {
            byte[] imageData = captureFrameAsBytes();
            if (imageData != null && imageData.length > 0) {
                BufferedImage image = ImageIO.read(new ByteArrayInputStream(imageData));
                return ImageIO.write(image, "png", new java.io.File(filePath));
            }
        } catch (Exception e) {
            log.error("保存图像失败: {}", e.getMessage(), e);
        }
        return false;
    }

    /**
     * 统计信息
     */
    public static CameraMonitorStats getMonitorStats() {
        return new CameraMonitorStats(
                isRunning(),
                cameraInitialized,
                useFallbackImage,
                captureCount.get(),
                errorImageCount.get(),
                lastCaptureTime.get(),
                listeners.size()
        );
    }

    public static class CameraMonitorStats {
        private final boolean running;
        private final boolean cameraInitialized;
        private final boolean useFallbackImage;
        private final long totalCaptures;
        private final long errorImageCount;
        private final long lastCaptureTime;
        private final int listenerCount;

        public CameraMonitorStats(boolean running, boolean cameraInitialized, boolean useFallbackImage,
                                  long totalCaptures, long errorImageCount, long lastCaptureTime, int listenerCount) {
            this.running = running;
            this.cameraInitialized = cameraInitialized;
            this.useFallbackImage = useFallbackImage;
            this.totalCaptures = totalCaptures;
            this.errorImageCount = errorImageCount;
            this.lastCaptureTime = lastCaptureTime;
            this.listenerCount = listenerCount;
        }

        // Getter方法
        public boolean isRunning() { return running; }
        public boolean isCameraInitialized() { return cameraInitialized; }
        public boolean isUseFallbackImage() { return useFallbackImage; }
        public long getTotalCaptures() { return totalCaptures; }
        public long getErrorImageCount() { return errorImageCount; }
        public long getLastCaptureTime() { return lastCaptureTime; }
        public int getListenerCount() { return listenerCount; }
    }
}