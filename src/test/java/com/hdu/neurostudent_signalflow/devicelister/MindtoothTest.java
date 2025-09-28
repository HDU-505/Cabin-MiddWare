package com.hdu.neurostudent_signalflow.devicelister;

import com.hdu.neurostudent_signalflow.devicelister.mindtooth.MindToothEnvInit;
import org.junit.jupiter.api.Test;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.context.annotation.Import;
import org.springframework.test.context.ContextConfiguration;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.*;
import java.util.stream.Collectors;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;


public class MindtoothTest {
    @Test
    void testMindToothEnvInit() throws InterruptedException {
        MindToothEnvInit envInit = new MindToothEnvInit();
        Thread thread = new Thread(envInit);
        thread.start();
        thread.join();
        System.out.println("test");
    }

    @Test
    public void testDataConsistency() throws IOException {
        // 1. 读取输入文件
        Path inputPath = Paths.get("D:\\\\Desktop\\\\code\\\\Cabin\\\\Cabin-MiddWare-DZL\\\\src\\\\main\\\\resources\\\\testData\\\\testInputData.txt");
        List<String> inputLines = Files.readAllLines(inputPath);

        // 2. 读取所有输出文件
        Path dir = inputPath.getParent() != null ? inputPath.getParent() : Paths.get(".");
        List<Path> outputFiles = Files.list(dir)
                .filter(p -> p.getFileName().toString().startsWith("testOutputDatapool-7-thread-"))
                .sorted(Comparator.comparing(Path::toString))
                .collect(Collectors.toList());

        List<String> outputLines = new ArrayList<>();
        for (Path out : outputFiles) {
            outputLines.addAll(Files.readAllLines(out));
        }

        // 3. 转成 List，并排序，保证可比对
        List<String> inputSorted = new ArrayList<>(inputLines);
        List<String> outputSorted = new ArrayList<>(outputLines);

        for (String line : outputSorted) {
            if (inputSorted.contains(line)) {
                inputSorted.remove(line); // 确保每个元素只匹配一次
            } else {
                System.out.println("输出文件中存在输入文件没有的行: " + line);
            }
        }
    }
}
