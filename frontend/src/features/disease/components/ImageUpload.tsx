'use client';
import React, { useRef, useState } from 'react';
import styles from './ImageUpload.module.css';
import { FarmOption } from '../types';
import { UploadCloud, Camera, RefreshCw, Sparkles, Image as ImageIcon, Leaf, Bug } from 'lucide-react';

interface ImageUploadProps {
  imagePreviewUrl: string | null;
  farmOptions: FarmOption[];
  selectedFarm: FarmOption | null;
  onImageSelect: (file: File) => void;
  onImageClear: () => void;
  onFarmSelect: (farm: FarmOption | null) => void;
  onStartAnalysis: () => void;
}

export const ImageUpload: React.FC<ImageUploadProps> = ({
  imagePreviewUrl,
  farmOptions,
  selectedFarm,
  onImageSelect,
  onImageClear,
  onFarmSelect,
  onStartAnalysis,
}) => {
  const [isDragOver, setIsDragOver] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const cameraInputRef = useRef<HTMLInputElement>(null);

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(true);
  };

  const handleDragLeave = () => {
    setIsDragOver(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      processFile(e.dataTransfer.files[0]);
    }
  };

  const processFile = (file: File) => {
    if (!file.type.startsWith('image/')) return;
    setIsLoading(true);
    // Instant processing with micro-task to allow browser to render UI feedback
    setTimeout(() => {
      onImageSelect(file);
      setIsLoading(false);
    }, 50);
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      processFile(e.target.files[0]);
      // Reset input value so re-selecting same file works
      e.target.value = '';
    }
  };

  const handleDropzoneClick = (e: React.MouseEvent) => {
    // If no image preview, clicking anywhere on dropzone opens file picker
    if (!imagePreviewUrl) {
      fileInputRef.current?.click();
    }
  };

  return (
    <div className={styles.container}>
      {/* Hidden File Inputs */}
      <input
        type="file"
        ref={fileInputRef}
        className={styles.hiddenInput}
        accept="image/*"
        onChange={handleFileChange}
      />
      <input
        type="file"
        ref={cameraInputRef}
        className={styles.hiddenInput}
        accept="image/*"
        capture="environment"
        onChange={handleFileChange}
      />

      {/* Dropzone Container */}
      <div
        className={`${styles.dropzone} ${isDragOver ? styles.dragOver : ''} ${imagePreviewUrl ? styles.hasImage : ''}`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={handleDropzoneClick}
        style={{ cursor: !imagePreviewUrl ? 'pointer' : 'default' }}
      >
        {isLoading ? (
          <div className={styles.loadingBox}>
            <div className={styles.spinner} />
            <p className={styles.loadingText}>Processing image...</p>
          </div>
        ) : imagePreviewUrl ? (
          <div className={styles.previewContainer}>
            <img src={imagePreviewUrl} alt="Crop Preview" className={styles.previewImage} />
            <div className={styles.previewOverlay}>
              <button
                type="button"
                className={styles.changeImageBtn}
                onClick={(e) => {
                  e.stopPropagation();
                  fileInputRef.current?.click();
                }}
              >
                <RefreshCw size={14} /> Change Photo
              </button>
              <button
                type="button"
                className={styles.clearBtn}
                onClick={(e) => {
                  e.stopPropagation();
                  onImageClear();
                }}
              >
                Remove
              </button>
            </div>
          </div>
        ) : (
          <div className={styles.uploadPrompt}>
            <div className={styles.illustration}>
              <div className={styles.glow} />
              <Camera size={36} className={`${styles.illustIcon} ${styles.icon1}`} />
              <Leaf size={24} className={`${styles.illustIcon} ${styles.icon2}`} />
              <Bug size={28} className={`${styles.illustIcon} ${styles.icon3}`} />
              <Sparkles size={20} className={`${styles.illustIcon} ${styles.icon4}`} />
            </div>
            <div className={styles.promptText}>
              <p className={styles.primaryText}>Upload Crop Image</p>
              <p className={styles.secondaryText}>Drag & drop or choose an image</p>
            </div>
            
            <div className={styles.actions} onClick={(e) => e.stopPropagation()}>
              <button
                type="button"
                className={styles.uploadBtn}
                onClick={() => fileInputRef.current?.click()}
              >
                <ImageIcon size={18} /> Upload Image
              </button>
              <button
                type="button"
                className={styles.captureBtn}
                onClick={() => cameraInputRef.current?.click()}
              >
                <Camera size={18} /> Capture Photo
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Optional Farm Selector (Always below image/upload) */}
      <div className={styles.farmSelectContainer}>
        <label className={styles.label}>Select a farm <span style={{opacity: 0.5}}>(Optional)</span></label>
        <select
          className={styles.select}
          value={selectedFarm?.id || ''}
          onChange={(e) => {
            const val = e.target.value;
            if (!val) onFarmSelect(null);
            else {
              const farm = farmOptions.find((f) => f.id === val);
              if (farm) onFarmSelect(farm);
            }
          }}
        >
          <option value="">Select a farm...</option>
          {farmOptions.map((farm) => (
            <option key={farm.id} value={farm.id}>
              {farm.name}
            </option>
          ))}
        </select>
      </div>

      {/* Analyze CTA Button (High prominence right under farm selector) */}
      <button
        type="button"
        className={`${styles.analyzeBtn} ${(!imagePreviewUrl || !selectedFarm) ? styles.analyzeBtnDisabled : ''}`}
        disabled={!imagePreviewUrl || !selectedFarm}
        style={{
          opacity: (!imagePreviewUrl || !selectedFarm) ? 0.5 : 1,
          cursor: (!imagePreviewUrl || !selectedFarm) ? 'not-allowed' : 'pointer'
        }}
        onClick={() => {
          if (!imagePreviewUrl || !selectedFarm) {
            alert('Please select an image and a farm context first.');
            return;
          }
          onStartAnalysis();
        }}
      >
        <Sparkles size={20} /> Analyze Crop
      </button>

      <div style={{ textAlign: 'center', marginTop: '16px', fontSize: '13px', color: 'rgba(255, 255, 255, 0.6)' }}>
        By continuing, you agree to our <span style={{ color: 'var(--color-primary)' }}>Terms of Use</span> and <span style={{ color: 'var(--color-primary)' }}>Privacy Policy</span>
      </div>
    </div>
  );
};
