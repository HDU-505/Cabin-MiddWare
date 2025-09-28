package com.hdu.neurostudent_signalflow.service.Impl;

import com.hdu.neurostudent_signalflow.config.ExperimentProperties;
import com.hdu.neurostudent_signalflow.config.ParadigmConfig;
import com.hdu.neurostudent_signalflow.devicelister.MindToothEnvInit;
import com.hdu.neurostudent_signalflow.entity.ParadigmTouchScreen;
import com.hdu.neurostudent_signalflow.experiment.ExperimentEvent;
import com.hdu.neurostudent_signalflow.experiment.ExperimentStateMachine;
import com.hdu.neurostudent_signalflow.service.ParadigmService;
import com.hdu.neurostudent_signalflow.utils.ConfigManager;
import com.hdu.neurostudent_signalflow.utils.IdGenerator;
import org.apache.commons.compress.archivers.zip.ZipArchiveEntry;
import org.apache.commons.compress.archivers.zip.ZipFile;
import org.apache.tomcat.util.http.fileupload.IOUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;

import java.io.*;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.Enumeration;
import java.util.List;

@Service
public class ParadigmServiceImpl implements ParadigmService {
    private ParadigmTouchScreen paradigmTouchScreenCahce;

    private static final Logger logger = LoggerFactory.getLogger(ParadigmServiceImpl.class);

    private final ExperimentStateMachine experimentStateMachine = ExperimentStateMachine.getInstance();


    public ParadigmServiceImpl() {
        paradigmTouchScreenCahce = new ParadigmTouchScreen();

    }

    /*
     *   上传文件
     * */
    @Override
    public boolean cacheFile(MultipartFile coverFile,MultipartFile paradigmFile) {
        // 将文件保存到本地缓存文件夹中，并记录下路径
        String projectPath = Paths.get("").toAbsolutePath().toString();
        String uploadDir = projectPath + "/uploads/";
        new File(uploadDir).mkdirs();
        try {
            //存储封面文件
            String fileOriginalName = coverFile.getOriginalFilename();
            String fileExtension = fileOriginalName.substring(fileOriginalName.lastIndexOf("."));
            String fileUUIDName = IdGenerator.generate20CharId() + fileExtension;
            String filePath = uploadDir + fileUUIDName;
            File file = new File(filePath);
            coverFile.transferTo(file);
            paradigmTouchScreenCahce.setCoverPath(filePath);

            //存储范式文件
            String fileOriginalName2 = paradigmFile.getOriginalFilename();
            String fileExtension2 = fileOriginalName2.substring(fileOriginalName2.lastIndexOf("."));
            String fileUUIDName2 = IdGenerator.generate20CharId() + fileExtension2;
            String filePath2 = uploadDir + fileUUIDName2;
            paradigmFile.transferTo(new File(filePath2));
            paradigmTouchScreenCahce.setFilePath(filePath2);

            return true;
        } catch (IOException e) {
            e.printStackTrace();
            return false;
        }
    }

    /*
     *  存储文件
     * */
    @Override
    public boolean storeFile(ParadigmTouchScreen paradigmTouchScreen) {
        //判断缓存文件是否存在
        if (paradigmTouchScreen == null)
            return false;
        // 判断paradigm是否为空
        if (paradigmTouchScreenCahce == null)
            return false;

        paradigmTouchScreen.setCoverPath(paradigmTouchScreenCahce.getCoverPath());
        paradigmTouchScreen.setFilePath(paradigmTouchScreenCahce.getFilePath());

        ConfigManager.addParadigmTouchScreen(paradigmTouchScreen);
        return true;
    }

    @Override
    public List<ParadigmTouchScreen> getAllParadigm() {
        // 遍历配置文件获取所有的范式信息
        try{
            List<ParadigmTouchScreen> paradigmTouchScreens = ConfigManager.getParadigmTouchScreens();

            return paradigmTouchScreens;
        }catch (Exception e){
            return null;
        }
    }

    /*
    *   选择本次实验所需的范式
    * */

    @Override
    public boolean selectParadigmById(String id) {
        // 遍历配置文件获取所有的范式信息
        List<ParadigmTouchScreen> paradigmTouchScreens = ConfigManager.getParadigmTouchScreens();
        for (ParadigmTouchScreen paradigmTouchScreen : paradigmTouchScreens) {
            if (paradigmTouchScreen.getId().equals(id)) {
                ParadigmConfig.PARADIGM = paradigmTouchScreen;
                return true;
            }
        }
        return false;
    }


    /*
    *   执行本次实验范式
    * */
    @Override
    public boolean executeParadigm(String experiment_id) {
        // 判断是否已经选择了范式
        if (ParadigmConfig.PARADIGM == null && experiment_id != null && !experiment_id.trim().isEmpty())
            return false;
        ExperimentProperties.experimentId = experiment_id;
        // 执行范式
        // 获取范式文件
        String filePath = ParadigmConfig.PARADIGM.getFilePath();
        // 创建临时目录
//        String tempDirPath = "H:\\doing\\NeuroStudent_SignalFlow\\NeuroStudent_SignalFlow\\temp";
//        // 测试阶段的目录
////        String tempDirPath = "D:\\code\\middleware\\temp";
//        Path tempDir = null;
//        try {
//            tempDir = Files.createDirectories(Paths.get(tempDirPath));
//            // 解压zip文件
//            try (ZipFile zipFile = new ZipFile(new File(filePath))) {
//                Enumeration<ZipArchiveEntry> entries = zipFile.getEntries();
//                while (entries.hasMoreElements()) {
//                    ZipArchiveEntry entry = entries.nextElement();
//                    if (entry.isDirectory()) {
//                        // 创建目录
//                        Path dirPath = tempDir.resolve(entry.getName());
//                        Files.createDirectories(dirPath);
//                        System.out.println("Created directory: " + dirPath);
//                    } else {
//                        // 创建文件
//                        Path filePath1 = tempDir.resolve(entry.getName());
//                        Files.createDirectories(filePath1.getParent());
//                        try (InputStream inputStream = zipFile.getInputStream(entry);
//                             FileOutputStream outputStream = new FileOutputStream(filePath1.toFile())) {
//                            IOUtils.copy(inputStream, outputStream);
//                        } catch (IOException e) {
//                            // 处理读取或写入文件时的异常
//                            System.out.println("Failed to extract file: " + entry.getName());
//                            e.printStackTrace();
//                        }
//                        System.out.println("Created file: " + filePath);
//                    }
//                }
//            }
//        } catch (IOException e) {
//            e.printStackTrace();
//        }
//
//        // 执行范式
//        // 检查文件夹中是否存在start.py文件,没有则返回False
//        File startFile = new File(tempDirPath + "/start.py");
//        System.out.println(tempDirPath + "/start.py");
//        if (!startFile.exists()) {
//            System.out.println("不存在启动文件");
//            return false;
//        }
        startEprimeFile(filePath);
        // 执行文件
        // 启动新线程运行 Python 脚本
//        Thread thread = new Thread(() -> {
//            try {
//                System.out.println("开始执行范式");
//                //开发阶段的环境
//                ProcessBuilder processBuilder = new ProcessBuilder("python", startFile.getAbsolutePath());
//                //测试阶段的环境
////                ProcessBuilder processBuilder = new ProcessBuilder("D:\\enviroment_program\\python39\\python", startFile.getAbsolutePath());
//                processBuilder.start();
//            } catch (Exception e) {
//                e.printStackTrace();
//            }
//        });
//        thread.start();
        return true;
    }

    private List<Process> processes = new ArrayList<>();


    public void startEprimeFile(String fileName){
        try {
            // 指定可执行文件的路径
            // 获取资源文件的路径
//            ClassPathResource resource = new ClassPathResource("SDK/EegAmpApp/startPython.bat");
//            Path exePath = Paths.get(resource.getURI());

            // 创建 ProcessBuilder 对象
//            // 未打包阶段
//            ProcessBuilder processBuilder = new ProcessBuilder(exePath.toString());
            // 开发阶段
            ProcessBuilder processBuilder = new ProcessBuilder(fileName);
            //测试阶段
//            ProcessBuilder processBuilder = new ProcessBuilder("H:\\environment\\SDK\\EegAmpApp\\startPython.bat");

            // 将标准错误流合并到标准输出流
            processBuilder.redirectErrorStream(true);

            // 启动外部应用程序
            Process process = processBuilder.start();
            processes.add(process);

            // 读取外部应用程序的输出流
            BufferedReader reader = new BufferedReader(new InputStreamReader(process.getInputStream()));
            String line;
            while ((line = reader.readLine()) != null) {
                logger.info("External application output: " + line);
            }

            // 等待外部应用程序退出
            int exitCode = process.waitFor();
            System.out.println("External application exited with code: " + exitCode);

            // 实验结束
            experimentStateMachine.handleEvent(ExperimentEvent.END_EXPERIMENT);
        } catch (IOException | InterruptedException e) {
            logger.error("范式启动失败,原因为："+e.getMessage());
            e.printStackTrace();
        }
    }


    /*
    *   根据Id返回范式信息
    * */
    @Override
    public ParadigmTouchScreen getParadigmById(String id) {
        // 遍历配置文件获取所有的范式信息
        List<ParadigmTouchScreen> paradigmTouchScreens = ConfigManager.getParadigmTouchScreens();
        for (ParadigmTouchScreen paradigmTouchScreen : paradigmTouchScreens) {
            if (paradigmTouchScreen.getId().equals(id)) {
                return paradigmTouchScreen;
            }
        }
        return null;
    }


}
