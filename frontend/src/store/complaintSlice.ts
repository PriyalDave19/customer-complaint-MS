import { createSlice, createAsyncThunk, type PayloadAction } from '@reduxjs/toolkit';
import axios from 'axios';

// Interfaces based on Backend Pydantic Schemas
export interface ComplaintData {
  source: string | null;
  customer_name: string | null;
  product_name: string | null;
  product_strength: string | null;
  batch_number: string | null;
  manufacturing_date: string | null;
  expiry_date: string | null;
  quantity_affected: number | null;
  complaint_type: string | null;
  complaint_date: string | null;
  description: string | null;
  severity: string | null;
  priority: string | null;
}

export interface RiskAssessmentData {
  risk_class: string | null;
  root_cause_hypothesis: string | null;
  capa_recommendation: string | null;
}

interface ComplaintState {
  formData: ComplaintData;
  riskAssessment: RiskAssessmentData | null;
  status: 'idle' | 'loading' | 'succeeded' | 'failed';
  error: string | null;
  extractionProgress: number; // 0 to 100
}

const initialFormData: ComplaintData = {
  source: null, customer_name: null, product_name: null, product_strength: null,
  batch_number: null, manufacturing_date: null, expiry_date: null, quantity_affected: null,
  complaint_type: null, complaint_date: null, description: null, severity: null, priority: null,
};

const initialState: ComplaintState = {
  formData: initialFormData,
  riskAssessment: null,
  status: 'idle',
  error: null,
  extractionProgress: 0,
};

export const extractComplaintData = createAsyncThunk(
  'complaint/extract',
  async ({ text, file }: { text: string, file: File | null }, { rejectWithValue }) => {
    try {
      const formData = new FormData();
      if (text) {
        formData.append('text', text);
      }
      if (file) {
        formData.append('file', file);
      }
      const response = await axios.post('http://localhost:8000/api/complaints/extract', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      return response.data; // { extracted_data, risk_analysis }
    } catch (err: any) {
      return rejectWithValue(err.response?.data?.detail || 'Extraction failed');
    }
  }
);

export const refineComplaintData = createAsyncThunk(
  'complaint/refine',
  async (payload: { current_data: ComplaintData, prompt: string }, { rejectWithValue }) => {
    try {
      const response = await axios.post('http://localhost:8000/api/complaints/refine', payload);
      return response.data;
    } catch (err: any) {
      return rejectWithValue(err.response?.data?.detail || 'Refinement failed');
    }
  }
);

export const saveComplaintData = createAsyncThunk(
  'complaint/save',
  async (data: { complaint: ComplaintData, risk: RiskAssessmentData | null }, { rejectWithValue }) => {
    try {
      const payload = {
        ...data.complaint,
        risk_assessment: data.risk
      };
      const response = await axios.post('http://localhost:8000/api/complaints/', payload);
      return response.data;
    } catch (err: any) {
      return rejectWithValue(err.response?.data?.detail || 'Save failed');
    }
  }
);

export const complaintSlice = createSlice({
  name: 'complaint',
  initialState,
  reducers: {
    updateFormField: (state, action: PayloadAction<{ field: keyof ComplaintData, value: any }>) => {
      state.formData[action.payload.field] = action.payload.value;
    },
    resetForm: (state) => {
      state.formData = initialFormData;
      state.riskAssessment = null;
      state.status = 'idle';
      state.error = null;
      state.extractionProgress = 0;
    },
    setExtractionProgress: (state, action: PayloadAction<number>) => {
      state.extractionProgress = action.payload;
    }
  },
  extraReducers: (builder) => {
    builder
      .addCase(extractComplaintData.pending, (state) => {
        state.status = 'loading';
        state.error = null;
        state.extractionProgress = 10;
      })
      .addCase(extractComplaintData.fulfilled, (state, action) => {
        state.status = 'succeeded';
        state.extractionProgress = 100;
        // Merge extracted data into formData, leaving existing fields intact if not overwritten by null
        const extracted = action.payload.extracted_data;
        Object.keys(extracted).forEach(key => {
          if (extracted[key] !== null) {
            (state.formData as any)[key] = extracted[key];
          }
        });
        state.riskAssessment = action.payload.risk_analysis;
      })
      .addCase(extractComplaintData.rejected, (state, action) => {
        state.status = 'failed';
        state.error = action.payload as string;
        state.extractionProgress = 0;
      })
      .addCase(refineComplaintData.pending, (state) => {
        state.status = 'loading';
        state.error = null;
        state.extractionProgress = 50;
      })
      .addCase(refineComplaintData.fulfilled, (state, action) => {
        state.status = 'succeeded';
        state.extractionProgress = 100;
        const extracted = action.payload.extracted_data;
        Object.keys(extracted).forEach(key => {
          if (extracted[key] !== null) {
            (state.formData as any)[key] = extracted[key];
          }
        });
        state.riskAssessment = action.payload.risk_analysis;
      })
      .addCase(refineComplaintData.rejected, (state, action) => {
        state.status = 'failed';
        state.error = action.payload as string;
        state.extractionProgress = 0;
      });
  },
});

export const { updateFormField, resetForm, setExtractionProgress } = complaintSlice.actions;

export default complaintSlice.reducer;
