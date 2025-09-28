package com.hdu.neurostudent_signalflow.utils;


import java.security.SecureRandom;
import java.util.UUID;
import java.util.concurrent.atomic.AtomicInteger;

public class IdGenerator {
    private static final String CHARACTERS = "0123456789";
    private static final SecureRandom random = new SecureRandom();
    // 自增序列，避免同一毫秒内重复
    private static final AtomicInteger counter = new AtomicInteger(0);

    public static String generate20CharId() {
        StringBuilder sb = new StringBuilder(20);
        for (int i = 0; i < 20; i++) {
            sb.append(CHARACTERS.charAt(random.nextInt(CHARACTERS.length())));
        }
        return sb.toString();
    }

    /**
     * 生成固定16位长度的实验ID
     * 格式：时间戳后6位 + 自增计数3位 + 随机数7位
     */
    public static String generateExperimentId() {
        // 时间戳后6位
        String timePart = String.valueOf(System.currentTimeMillis() % 1_000_000);

        // 计数器（取 3 位，不足补0）
        int count = counter.updateAndGet(i -> (i >= 999 ? 0 : i + 1));
        String countPart = String.format("%03d", count);

        // 随机部分（取 UUID hash 的绝对值后 7 位）
        String randomPart = String.format("%07d", Math.abs(UUID.randomUUID().hashCode()) % 10_000_000);

        return timePart + countPart + randomPart; // 总长度 16
    }
}
