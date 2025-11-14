package com.hdu.neurostudent_signalflow.service;

import com.hdu.neurostudent_signalflow.entity.ParadigmTouchScreen;
import org.springframework.web.multipart.MultipartFile;

import java.util.List;

public interface ParadigmService {
    boolean cacheFile(MultipartFile coverFile,MultipartFile paradigmFile);

    boolean storeFile(ParadigmTouchScreen paradigmTouchScreen);

    List<ParadigmTouchScreen> getAllParadigm();

    boolean selectParadigmById(String id);

    boolean executeParadigm(String experiment_id);

    ParadigmTouchScreen getParadigmById(String id);

    void stopParadigm();
}
