package com.hdu.neurostudent_signalflow.monitor;

public class BaseMonitor {
    public interface MonitorCaptureListener {
        void onCaptured(String type, byte[] imageData);
    }
}
