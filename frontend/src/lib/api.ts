import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

export const apiClient = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

apiClient.interceptors.request.use((config) => {
    if (typeof window !== "undefined") {
        const token = localStorage.getItem("token");
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
    }
    return config;
});

// Add a response interceptor to handle 401 Unauthorized
apiClient.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response && error.response.status === 401) {
            // Token is invalid or expired
            if (typeof window !== "undefined") {
                localStorage.removeItem("token");
                window.location.href = "/";
            }
        }
        return Promise.reject(error);
    }
);

export const verifyApi = {
    uploadDocument: async (file: File) => {
        const formData = new FormData();
        formData.append('file', file);
        
        // Use apiClient to ensure interceptors run (auth header + 401 redirect)
        const response = await apiClient.post(`/verify/upload`, formData, {
            headers: {
                'Content-Type': 'multipart/form-data',
            },
        });
        return response.data; // { job_id: string, status: string }
    },
    
    getJobStatus: async (jobId: string) => {
        const response = await apiClient.get(`/verify/status/${jobId}`);
        return response.data;
    }
};
