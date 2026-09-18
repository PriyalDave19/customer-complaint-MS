import { useSelector, useDispatch } from 'react-redux';
import type { RootState } from '../store';
import { updateFormField, resetForm, saveComplaintData } from '../store/complaintSlice';
import { Save, RotateCcw } from 'lucide-react';

const ComplaintForm = () => {
  const dispatch = useDispatch<any>();
  const { formData, riskAssessment } = useSelector((state: RootState) => state.complaint);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    dispatch(updateFormField({ field: e.target.name as any, value: e.target.value }));
  };

  const handleSave = () => {
    dispatch(saveComplaintData({ complaint: formData, risk: riskAssessment }));
    alert('Complaint saved successfully (mock check backend logs)');
  };

  const InputField = ({ label, name, type = 'text', placeholder = 'Awaiting AI extraction...' }: any) => (
    <div className="flex flex-col space-y-1">
      <label className="text-sm font-semibold text-gray-700">{label}</label>
      <input
        type={type}
        name={name}
        value={formData[name as keyof typeof formData] || ''}
        onChange={handleChange}
        placeholder={placeholder}
        className="px-3 py-2 border border-gray-200 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 bg-white shadow-sm text-sm"
      />
    </div>
  );

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6 lg:col-span-2 flex flex-col h-full overflow-y-auto">
      <div className="flex justify-between items-center border-b border-gray-100 pb-4 mb-6">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Log Customer Complaint</h2>
          <p className="text-sm text-gray-500 mt-1">API & FDF Quality Assurance Module</p>
        </div>
        <span className="px-3 py-1 bg-yellow-50 text-yellow-700 text-xs font-semibold rounded-full border border-yellow-200">
          Pending Triage
        </span>
      </div>

      <div className="space-y-8 flex-1">
        {/* Section 1 */}
        <section>
          <h3 className="text-xs font-bold text-gray-400 uppercase tracking-wider mb-4">1. Origin & Customer Details</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <InputField label="Complaint Source" name="source" />
            <InputField label="Customer Name" name="customer_name" />
          </div>
        </section>

        {/* Section 2 */}
        <section>
          <h3 className="text-xs font-bold text-gray-400 uppercase tracking-wider mb-4">2. Product & Batch Identification</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <InputField label="Product Name" name="product_name" />
            <InputField label="Product Strength/Grade" name="product_strength" />
            <InputField label="Batch/Lot Number" name="batch_number" />
            <InputField label="Manufacturing Date" name="manufacturing_date" type="date" />
            <InputField label="Expiry Date" name="expiry_date" type="date" />
            <div className="flex flex-col space-y-1">
              <label className="text-sm font-semibold text-gray-700">Quantity Affected</label>
              <div className="relative">
                <input
                  type="number"
                  name="quantity_affected"
                  value={formData.quantity_affected || ''}
                  onChange={handleChange}
                  placeholder="Awaiting AI extraction..."
                  className="w-full px-3 py-2 border border-gray-200 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 bg-white shadow-sm text-sm pr-10"
                />
                <span className="absolute right-3 top-2 text-gray-400 text-sm">kg</span>
              </div>
            </div>
          </div>
        </section>

        {/* Section 3 */}
        <section>
          <h3 className="text-xs font-bold text-gray-400 uppercase tracking-wider mb-4">3. Complaint Details</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <InputField label="Complaint Type" name="complaint_type" />
            <InputField label="Complaint Date" name="complaint_date" type="date" />
            <div className="col-span-1 md:col-span-2 flex flex-col space-y-1">
              <label className="text-sm font-semibold text-gray-700">Detailed Complaint Description</label>
              <textarea
                name="description"
                value={formData.description || ''}
                onChange={handleChange as any}
                placeholder="Awaiting AI extraction..."
                rows={4}
                className="px-3 py-2 border border-gray-200 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 bg-white shadow-sm text-sm resize-none"
              />
            </div>
          </div>
        </section>

        {/* Section 4 */}
        <section>
          <h3 className="text-xs font-bold text-gray-400 uppercase tracking-wider mb-4">4. Initial Assessment & Priority</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="flex flex-col space-y-1">
              <label className="text-sm font-semibold text-gray-700">Initial Severity</label>
              <select
                name="severity"
                value={formData.severity || ''}
                onChange={handleChange}
                className="px-3 py-2 border border-gray-200 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 bg-white shadow-sm text-sm"
              >
                <option value="">Awaiting AI extraction...</option>
                <option value="Critical">Critical</option>
                <option value="Major">Major</option>
                <option value="Minor">Minor</option>
              </select>
            </div>
            <div className="flex flex-col space-y-1">
              <label className="text-sm font-semibold text-gray-700">Priority</label>
              <select
                name="priority"
                value={formData.priority || ''}
                onChange={handleChange}
                className="px-3 py-2 border border-gray-200 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 bg-white shadow-sm text-sm"
              >
                <option value="">Awaiting AI extraction...</option>
                <option value="High">High</option>
                <option value="Medium">Medium</option>
                <option value="Low">Low</option>
              </select>
            </div>
          </div>
        </section>
      </div>

      <div className="mt-8 pt-6 border-t border-gray-100 flex justify-between items-center">
        <button
          onClick={() => dispatch(resetForm())}
          className="flex items-center px-4 py-2 text-gray-600 bg-gray-50 border border-gray-200 rounded-md hover:bg-gray-100 transition-colors text-sm font-medium"
        >
          <RotateCcw className="w-4 h-4 mr-2" />
          Reset Form
        </button>
        <button
          onClick={handleSave}
          className="flex items-center px-6 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700 transition-colors text-sm font-medium shadow-sm"
        >
          <Save className="w-4 h-4 mr-2" />
          Save Complaint
        </button>
      </div>
    </div>
  );
};

export default ComplaintForm;
