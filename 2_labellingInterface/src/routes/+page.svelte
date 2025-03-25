<script lang="ts">
    import { onMount } from 'svelte';
  
    // TypeScript interfaces
    interface LabelDefinition {
      name: string;
      color: string;
    }

    interface FilesDictionary {
      [key: string]: string[];
    }
    
    // Loading state
    let isLoadingImages: boolean = false;
    let isLoadingTxtFiles: boolean = false;
    
    // State for all unique labels from TXT files
    let allUniqueLabels: string[] = [];
  
    let filesDict: FilesDictionary = {};
    let uploadedFiles: File[] = [];
    let totalFileCount: number = 0;
    let fileInput: HTMLInputElement;
    let txtFolderInput: HTMLInputElement;
    let currentView: 'main' | 'subfolder' = 'main';
    let selectedSubfolder: string = '';
    let fileObjects: Map<string, File> = new Map();
    let txtFiles: Map<string, string[]> = new Map();
    let txtFolderSelected: boolean = false;
    let imagesDirectorySelected: boolean = false;
    
    // Label-related state
    let labels: LabelDefinition[] = [];
    let newLabelName: string = '';
    let newLabelColor: string = '#ff0000';
    let activeLabel: LabelDefinition | null = null;
    let selectedImages: {[key: string]: LabelDefinition} = {};
    let firstSelectedImage: string | null = null;
  
    // Fixed color palette for consistency
    const colorPalette: string[] = [
      "#FF0000", // Red
      "#0000FF", // Blue
      "#00FF00", // Green
      "#FFFF00", // Yellow
      "#FF00FF", // Magenta
      "#00FFFF", // Cyan
      "#FF8000", // Orange
      "#8000FF", // Purple
      "#0080FF", // Sky Blue
      "#FF0080", // Pink
      "#80FF00", // Lime
      "#00FF80", // Spring Green
      "#FF8080", // Light Red
      "#8080FF", // Light Blue
      "#80FF80", // Light Green
      "#FFFF80", // Light Yellow
      "#FF80FF", // Light Magenta
      "#80FFFF", // Light Cyan
      "#804000", // Brown
      "#408000"  // Dark Green
    ];
  
    // Add more colors if needed by programmatically generating them
    function expandColorPalette(baseColors: string[], totalNeeded: number): string[] {
      const colors = [...baseColors];
      
      if (baseColors.length >= totalNeeded) {
        return baseColors.slice(0, totalNeeded);
      }
      
      // Generate additional colors with varying hues
      for (let i = colors.length; i < totalNeeded; i++) {
        const hue = (i * 137) % 360; // Golden angle to get well-distributed colors
        const saturation = 70 + (i % 3) * 10; // 70%, 80%, 90%
        const lightness = 45 + (i % 4) * 5; // 45%, 50%, 55%, 60%
        colors.push(`hsl(${hue}, ${saturation}%, ${lightness}%)`);
      }
      
      return colors;
    }
  
    // Persistence for directories - Save data to localStorage
    function saveToLocalStorage(): void {
      // Save files dictionary structure
      if (Object.keys(filesDict).length > 0) {
        localStorage.setItem('filesDict', JSON.stringify(filesDict));
      }
      
      // Save label definitions
      if (labels.length > 0) {
        localStorage.setItem('labels', JSON.stringify(labels));
      }
      
      // Save selected images with their labels
      if (Object.keys(selectedImages).length > 0) {
        // We need to convert the selectedImages object to a serializable format
        // (because it contains label objects as values)
        const serializableSelectedImages: {[key: string]: string} = {};
        for (const [imgPath, label] of Object.entries(selectedImages)) {
          serializableSelectedImages[imgPath] = label.name; // Store just the label name
        }
        localStorage.setItem('selectedImages', JSON.stringify(serializableSelectedImages));
      }
      
      // Save TXT file contents
      if (txtFiles.size > 0) {
        const txtFilesObj: {[key: string]: string[]} = {};
        txtFiles.forEach((value, key) => {
          txtFilesObj[key] = value;
        });
        localStorage.setItem('txtFiles', JSON.stringify(txtFilesObj));
      }
      
      // Save current view and selected subfolder
      localStorage.setItem('currentView', currentView);
      if (selectedSubfolder) {
        localStorage.setItem('selectedSubfolder', selectedSubfolder);
      }
      
      // Save unique labels
      if (allUniqueLabels.length > 0) {
        localStorage.setItem('allUniqueLabels', JSON.stringify(allUniqueLabels));
      }
      
      // Save txtFolderSelected state
      localStorage.setItem('txtFolderSelected', JSON.stringify(txtFolderSelected));
      
      // Save imagesDirectorySelected state
      localStorage.setItem('imagesDirectorySelected', JSON.stringify(imagesDirectorySelected));
      
      // Save total file count
      localStorage.setItem('totalFileCount', totalFileCount.toString());
    }
  
    // Try to restore data from localStorage
    function loadFromLocalStorage(): void {
      try {
        // Restore filesDict if available
        const savedFilesDict = localStorage.getItem('filesDict');
        if (savedFilesDict) {
          filesDict = JSON.parse(savedFilesDict);
        }
        
        // Restore labels
        const savedLabels = localStorage.getItem('labels');
        if (savedLabels) {
          labels = JSON.parse(savedLabels);
        }
        
        // Restore TXT files
        const savedTxtFiles = localStorage.getItem('txtFiles');
        if (savedTxtFiles) {
          const txtFilesObj = JSON.parse(savedTxtFiles);
          txtFiles = new Map(Object.entries(txtFilesObj));
        }
        
        // Restore view state
        const savedView = localStorage.getItem('currentView');
        if (savedView && (savedView === 'main' || savedView === 'subfolder')) {
          currentView = savedView;
        }
        
        const savedSubfolder = localStorage.getItem('selectedSubfolder');
        if (savedSubfolder) {
          selectedSubfolder = savedSubfolder;
        }
        
        // Restore unique labels
        const savedUniqueLabels = localStorage.getItem('allUniqueLabels');
        if (savedUniqueLabels) {
          allUniqueLabels = JSON.parse(savedUniqueLabels);
        }
        
        // Restore txtFolderSelected
        const savedTxtFolderSelected = localStorage.getItem('txtFolderSelected');
        if (savedTxtFolderSelected) {
          txtFolderSelected = JSON.parse(savedTxtFolderSelected);
        }
        
        // Restore imagesDirectorySelected
        const savedImagesDirectorySelected = localStorage.getItem('imagesDirectorySelected');
        if (savedImagesDirectorySelected) {
          imagesDirectorySelected = JSON.parse(savedImagesDirectorySelected);
        }
        
        // Restore total file count
        const savedTotalFileCount = localStorage.getItem('totalFileCount');
        if (savedTotalFileCount) {
          totalFileCount = parseInt(savedTotalFileCount, 10);
        }
        
        // We'll restore selectedImages after other data is loaded
      } catch (error) {
        console.error('Error loading from localStorage:', error);
      }
    }
  
    async function handleFileSelect(event: Event): Promise<void> {
      const target = event.target as HTMLInputElement;
      const files = target.files;
      
      if (!files || files.length === 0) {
        return;
      }
      
      // Start loading
      isLoadingImages = true;
      
      try {
        // Clear previous data
        filesDict = {};
        fileObjects = new Map();
        uploadedFiles = Array.from(files);
        totalFileCount = files.length;
        
        // Process the uploaded files
        await processFiles(uploadedFiles);
        
        // Reset view to main
        currentView = 'main';
        
        // Set directory selected state to true
        imagesDirectorySelected = true;
        
        // Use unique labels from TXT files as default labels
        if (labels.length === 0 && allUniqueLabels.length > 0) {
          const expandedPalette = expandColorPalette(colorPalette, allUniqueLabels.length);
          labels = allUniqueLabels.map((name, index) => ({
            name,
            color: expandedPalette[index % expandedPalette.length]
          }));
        }
        
        // Save to localStorage
        saveToLocalStorage();
      } catch (error) {
        console.error('Error loading directory:', error);
      } finally {
        // End loading regardless of outcome
        isLoadingImages = false;
      }
    }
  
    async function handleTxtFolderSelect(event: Event): Promise<void> {
      const target = event.target as HTMLInputElement;
      const files = target.files;
      
      if (!files || files.length === 0) {
        return;
      }
      
      // Start loading
      isLoadingTxtFiles = true;
      
      try {
        // Clear previous txt files
        txtFiles = new Map();
        allUniqueLabels = [];
        const tempUniqueLabels = new Set<string>();
        
        // Process each txt file
        for (let i = 0; i < files.length; i++) {
          const file = files[i];
          if (file.name.endsWith('.txt')) {
            const fileName = file.name.slice(0, -4); // Remove .txt extension
            
            // Read file content
            try {
              const content = await readFileContent(file);
              const lines = content.split('\n').map(line => line.trim()).filter(line => line);
              txtFiles.set(fileName, lines);
              
              // Collect unique labels from this file (excluding NIL)
              lines.forEach(line => {
                // Only add non-NIL labels to the unique labels set
                if (line && line !== "NIL") {
                  tempUniqueLabels.add(line);
                }
              });
            } catch (error) {
              console.error(`Error reading ${file.name}:`, error);
            }
          }
        }
        
        // Add a slight delay to allow UI to update and show loading animation
        await new Promise(resolve => setTimeout(resolve, 300));
        
        // Convert Set to array for reactivity
        allUniqueLabels = [...tempUniqueLabels];
        txtFolderSelected = true;
        
        // Save to localStorage
        saveToLocalStorage();
      } catch (error) {
        console.error('Error loading TXT files:', error);
      } finally {
        // End loading regardless of outcome
        isLoadingTxtFiles = false;
      }
    }
    
    function readFileContent(file: File): Promise<string> {
      return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = (event) => {
          if (event.target && typeof event.target.result === 'string') {
            resolve(event.target.result);
          } else {
            reject(new Error('Failed to read file content'));
          }
        };
        reader.onerror = (error) => reject(error);
        reader.readAsText(file);
      });
    }
  
    async function processFiles(files: File[]): Promise<void> {
      // Store file objects for later use
      for (const file of files) {
        fileObjects.set(file.webkitRelativePath, file);
      }
  
      // Group files by their parent directory
      for (const file of files) {
        // Get the file path relative to the selected directory
        const path = file.webkitRelativePath;
        
        // Split the path into parts
        const pathParts = path.split('/');
        
        // We need at least 3 parts: main-dir/video-dir/image.ext
        if (pathParts.length >= 3) {
          const videoFolder = pathParts[1];
          
          // Initialize the array for this video folder if it doesn't exist
          if (!filesDict[videoFolder]) {
            filesDict[videoFolder] = [];
          }
          
          // Add the file path (video-dir/image.ext) to the array
          filesDict[videoFolder].push(`${videoFolder}/${pathParts[2]}`);
        }
      }
      
      // Sort the files in each subfolder
      Object.keys(filesDict).forEach(folder => {
        if (filesDict[folder]) {
          filesDict[folder].sort();
        }
      });
      
      // Add a slight delay to allow UI to update and show loading animation
      await new Promise(resolve => setTimeout(resolve, 300));
      
      // Trigger UI update
      filesDict = { ...filesDict };
    }
  
    function clearFiles(): void {
      fileInput.value = '';
      filesDict = {};
      uploadedFiles = [];
      fileObjects = new Map();
      currentView = 'main';
      selectedImages = {};
      firstSelectedImage = null;
      imagesDirectorySelected = false;
      totalFileCount = 0;
      
      // Clear localStorage for image-related data
      localStorage.removeItem('filesDict');
      localStorage.removeItem('selectedImages');
      localStorage.removeItem('currentView');
      localStorage.removeItem('selectedSubfolder');
      localStorage.removeItem('imagesDirectorySelected');
      localStorage.removeItem('totalFileCount');
    }
    
    function clearTxtFolder(): void {
      txtFolderInput.value = '';
      txtFiles = new Map();
      allUniqueLabels = [];
      labels = []; // Reset labels to empty
      txtFolderSelected = false;
      
      // Clear localStorage for txt-related data
      localStorage.removeItem('txtFiles');
      localStorage.removeItem('allUniqueLabels');
      localStorage.removeItem('txtFolderSelected');
      localStorage.removeItem('labels');
    }
    
    function viewSubfolder(subfolder: string): void {
      selectedSubfolder = subfolder;
      currentView = 'subfolder';
      selectedImages = {};
      firstSelectedImage = null;
      
      // Import labels from TXT file if available
      if (txtFolderSelected && hasTxtFile(subfolder)) {
        importTxtLabelsAsColors();
      }
      
      // Save current view state
      saveToLocalStorage();
    }
    
    function backToMain(): void {
      currentView = 'main';
      saveToLocalStorage();
    }
    
    // Navigation between videos
    function getAdjacentSubfolder(direction: 'prev' | 'next'): string | null {
      // Get all subfolder names and sort them
      const allSubfolders = Object.keys(filesDict).sort();
      const currentIndex = allSubfolders.indexOf(selectedSubfolder);
      
      if (currentIndex === -1) return null; // Shouldn't happen

      if (direction === 'prev') {
        // Get previous, or wrap around to the last
        return currentIndex > 0 ? allSubfolders[currentIndex - 1] : allSubfolders[allSubfolders.length - 1];
      } else {
        // Get next, or wrap around to the first
        return currentIndex < allSubfolders.length - 1 ? allSubfolders[currentIndex + 1] : allSubfolders[0];
      }
    }

    function goToPreviousVideo(): void {
      const prevSubfolder = getAdjacentSubfolder('prev');
      if (prevSubfolder) {
        viewSubfolder(prevSubfolder);
      }
    }

    function goToNextVideo(): void {
      const nextSubfolder = getAdjacentSubfolder('next');
      if (nextSubfolder) {
        viewSubfolder(nextSubfolder);
      }
    }
    
    function getImageUrl(filePath: string): string | null {
      if (uploadedFiles.length === 0) return null;
      
      const fullPath = `${uploadedFiles[0].webkitRelativePath.split('/')[0]}/${filePath}`;
      const file = fileObjects.get(fullPath);
      
      if (file && isImageFile(file.name)) {
        // Create object URL if it doesn't exist yet
        if (!(file as any)._objectUrl) {
          (file as any)._objectUrl = URL.createObjectURL(file);
        }
        return (file as any)._objectUrl;
      }
      return null;
    }
    
    function isImageFile(filename: string): boolean {
      const imageExtensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.svg'];
      const lowerFilename = filename.toLowerCase();
      return imageExtensions.some(ext => lowerFilename.endsWith(ext));
    }
    
    function hasTxtFile(folderName: string): boolean {
      return txtFiles.has(folderName);
    }
    
    function getTxtFileContent(folderName: string): string[] {
      return txtFiles.get(folderName) || [];
    }
    
    // Modified function to import labels, handling NIL labels specially
    function importTxtLabelsAsColors(): void {
      if (!selectedSubfolder || !hasTxtFile(selectedSubfolder)) return;
      
      const txtContent = getTxtFileContent(selectedSubfolder);
      if (!txtContent.length) return;
      
      // Get non-NIL labels from the TXT file
      const uniqueLabels = [...new Set(txtContent.filter(label => label !== "NIL"))];
      
      // Add these as actual labels with colors if they don't exist already
      uniqueLabels.forEach((labelName, index) => {
        if (!labels.some(l => l.name === labelName)) {
          // Get color from palette or generate new one
          const expandedPalette = expandColorPalette(colorPalette, uniqueLabels.length);
          const colorIndex = labels.length; // Use current label count as index
          
          labels = [...labels, { 
            name: labelName, 
            color: expandedPalette[colorIndex % expandedPalette.length]
          }];
        }
      });
      
      // Create a temporary map of old selected images to preserve those not in TXT
      const oldSelectedImages = {...selectedImages};
      
      // Reset selectedImages before applying labels from TXT file
      selectedImages = {};
      
      // Apply labels to images based on TXT file
      // Special handling for NIL labels - they don't get colored borders
      if (filesDict[selectedSubfolder]) {
        filesDict[selectedSubfolder].forEach((filePath, index) => {
          if (index < txtContent.length) {
            const labelName = txtContent[index];
            if (labelName !== "NIL") {
              const label = labels.find(l => l.name === labelName);
              if (label) {
                selectedImages[filePath] = label;
              }
            }
            // For NIL labels, we don't add them to selectedImages
          }
        });
      }
      
      // Update reactivity
      labels = [...labels];
      selectedImages = {...selectedImages};
      
      // Save to localStorage
      saveToLocalStorage();
    }
    
    // Label-related functions
    function addLabel(): void {
      if (newLabelName.trim()) {
        // Get appropriate color from palette
        const expandedPalette = expandColorPalette(colorPalette, labels.length + 1);
        const color = expandedPalette[labels.length % expandedPalette.length];
        
        labels = [...labels, { name: newLabelName.trim(), color: color }];
        newLabelName = '';
        
        // Save to localStorage
        saveToLocalStorage();
      }
    }
    
    // No longer used, but kept for compatibility
    function getRandomColor(): string {
      const expandedPalette = expandColorPalette(colorPalette, labels.length + 1);
      return expandedPalette[labels.length % expandedPalette.length];
    }
    
    function setActiveLabel(label: LabelDefinition): void {
      activeLabel = label;
      firstSelectedImage = null; // Reset selection start
    }
    
    function toggleSelection(imagePath: string, event: MouseEvent): void {
      if (!activeLabel) return; // No active label selected
      
      if (event.shiftKey && firstSelectedImage !== null) {
        // Shift-clicked: Select the range of images
        if (filesDict[selectedSubfolder]) {
          const currentFiles = filesDict[selectedSubfolder];
          const firstIndex = currentFiles.indexOf(firstSelectedImage);
          const currentIndex = currentFiles.indexOf(imagePath);
          
          if (firstIndex !== -1 && currentIndex !== -1) {
            const rangeStart = Math.min(firstIndex, currentIndex);
            const rangeEnd = Math.max(firstIndex, currentIndex);
            
            // Select all images in the range
            for (let i = rangeStart; i <= rangeEnd; i++) {
              const img = currentFiles[i];
              selectedImages[img] = activeLabel;
            }
          }
        }
      } else {
        // Regular click: Toggle the current image
        if (selectedImages[imagePath] === activeLabel) {
          // If already has this label, remove it
          delete selectedImages[imagePath];
        } else {
          // Assign the active label
          selectedImages[imagePath] = activeLabel;
        }
        
        // Set the first selected image for the next shift-click
        firstSelectedImage = imagePath;
      }
      
      // Create a new object to trigger reactivity
      selectedImages = {...selectedImages};
      
      // Save to localStorage
      saveToLocalStorage();
    }
    
    function removeLabel(index: number): void {
      // Remove this label from all images
      const labelToRemove = labels[index];
      
      for (let img in selectedImages) {
        if (selectedImages[img] === labelToRemove) {
          delete selectedImages[img];
        }
      }
      
      // Remove the label itself
      labels = labels.filter((_, i) => i !== index);
      
      // If the active label was removed, set active to null
      if (activeLabel === labelToRemove) {
        activeLabel = null;
      }
      
      // Create a new object to trigger reactivity
      selectedImages = {...selectedImages};
      
      // Save to localStorage
      saveToLocalStorage();
    }
    
    // Helper function to determine text color based on background brightness
    function getBrightness(hexColor: string): number {
      // For HSL colors
      if (hexColor.startsWith('hsl')) {
        // Extract lightness from hsl(h, s%, l%)
        const match = hexColor.match(/hsl\(\s*\d+\s*,\s*\d+%\s*,\s*(\d+)%\s*\)/);
        if (match && match[1]) {
          const lightness = parseInt(match[1], 10);
          return lightness > 50 ? 255 : 0;
        }
        return 128; // Default if parsing fails
      }
      
      // For hex colors
      hexColor = hexColor.replace('#', '');
      
      // Handle shorthand hex color
      if (hexColor.length === 3) {
        hexColor = hexColor.split('').map(c => c + c).join('');
      }
      
      const r = parseInt(hexColor.substr(0, 2), 16);
      const g = parseInt(hexColor.substr(2, 2), 16);
      const b = parseInt(hexColor.substr(4, 2), 16);
      
      // Calculate brightness (perceived luminance)
      return (r * 299 + g * 587 + b * 114) / 1000;
    }
    
    // Save results to a text file
    function saveResults(): void {
      // Create labels array where each line corresponds to an image
      const labelLines: string[] = [];
      const subfolder = selectedSubfolder;
      
      if (!filesDict[subfolder]) return;
      
      const images = filesDict[subfolder];
      
      // For each image, add either the label name or "NIL"
      images.forEach(imagePath => {
        if (selectedImages[imagePath]) {
          labelLines.push(selectedImages[imagePath].name);
        } else {
          labelLines.push("NIL");
        }
      });
      
      // Create text content (one label per line)
      const textContent = labelLines.join('\n');
      
      // Create a blob and download link
      const blob = new Blob([textContent], { type: "text/plain" });
      const url = URL.createObjectURL(blob);
      
      // Create download link and trigger download
      const a = document.createElement("a");
      a.href = url;
      a.download = `${selectedSubfolder}.txt`;
      document.body.appendChild(a);
      a.click();
      
      // Clean up
      URL.revokeObjectURL(url);
      document.body.removeChild(a);
      
      // Update TXT file content in memory
      txtFiles.set(selectedSubfolder, labelLines);
      
      // Save to localStorage
      saveToLocalStorage();
    }
    
    // Try to restore selectedImages after other data is loaded
    function restoreSelectedImages(): void {
      try {
        // Restore selected images (needs to happen after labels are loaded)
        const savedSelectedImages = localStorage.getItem('selectedImages');
        if (savedSelectedImages && labels.length > 0) {
          const serializedImages = JSON.parse(savedSelectedImages);
          
          // Convert back to proper format with label objects
          selectedImages = {};
          for (const [imgPath, labelName] of Object.entries(serializedImages)) {
            const label = labels.find(l => l.name === labelName);
            if (label) {
              selectedImages[imgPath] = label;
            }
          }
        }
      } catch (error) {
        console.error('Error restoring selectedImages:', error);
      }
    }
    
    // Clean up object URLs when component is destroyed
    onMount(() => {
      // Try to load data from localStorage
      loadFromLocalStorage();
      
      // Restore selectedImages (after labels are loaded)
      restoreSelectedImages();
      
      // Cleanup on unmount
      return () => {
        // Revoke all object URLs
        fileObjects.forEach((file, path) => {
          if ((file as any)._objectUrl) {
            URL.revokeObjectURL((file as any)._objectUrl);
          }
        });
      };
    });
  </script>

<main>
    <h1>Labelling Interface</h1>
    
    <div class="input-container">
      <div class="file-input-container">
        <input 
          bind:this={fileInput}
          type="file" 
          webkitdirectory={true}
          directory={true}
          multiple 
          on:change={handleFileSelect}
          id="directory-input"
        />
        <label for="directory-input" class="file-input-label">
          {#if isLoadingImages}
            <span class="loading-spinner"></span> Loading Images...
          {:else}
            Select Directory
          {/if}
        </label>
        
        {#if imagesDirectorySelected}
          <button class="clear-button" on:click={clearFiles}>Clear</button>
        {/if}
      </div>
      
      <div class="file-input-container">
        <input 
          bind:this={txtFolderInput}
          type="file" 
          webkitdirectory={true}
          directory={true}
          multiple 
          on:change={handleTxtFolderSelect}
          id="txt-folder-input"
        />
        <label for="txt-folder-input" class="file-input-label txt-folder-label">
          {#if isLoadingTxtFiles}
            <span class="loading-spinner"></span> Loading TXT Files...
          {:else}
            Select TXT Folder
          {/if}
        </label>
        
        {#if txtFolderSelected}
          <button class="clear-button" on:click={clearTxtFolder}>Clear</button>
        {/if}
      </div>
      
      {#if txtFolderSelected && allUniqueLabels.length > 0}
        <div class="unique-labels-container">
          <h4>Unique Labels Found in TXT Files:</h4>
          <div class="unique-labels-list">
            {#each allUniqueLabels as label}
              <span class="unique-label-item">{label}</span>
            {/each}
          </div>
        </div>
      {/if}
    </div>
    
    {#if imagesDirectorySelected && Object.keys(filesDict).length > 0}
      <h2>Selected Directory</h2>
      <p class="file-count">Total files: {totalFileCount}</p>
      
      {#if currentView === 'main'}
        <!-- Main view - table of subfolders -->
        <div class="subfolder-list">
          <h3>Subfolders</h3>
          <table class="subfolder-table">
            <thead>
              <tr>
                <th>Subfolder Name</th>
                <th>Number of Images</th>
                {#if txtFolderSelected}
                  <th>TXT File</th>
                {/if}
              </tr>
            </thead>
            <tbody>
              {#each Object.keys(filesDict).sort() as subfolder}
                <tr class="subfolder-row" on:click={() => viewSubfolder(subfolder)}>
                  <td>
                    <div class="folder-name-cell">
                      <span class="folder-icon">📁</span>
                      <span>{subfolder}</span>
                    </div>
                  </td>
                  <td class="image-count-cell">{filesDict[subfolder]?.length || 0}</td>
                  {#if txtFolderSelected}
                    <td class="txt-status-cell">
                      {#if hasTxtFile(subfolder)}
                        <span class="txt-exists">✅</span>
                      {:else}
                        <span class="txt-missing">❌</span>
                      {/if}
                    </td>
                  {/if}
                </tr>
              {/each}
            </tbody>
          </table>
        </div>
      {:else if currentView === 'subfolder'}
        <!-- Subfolder view -->
        <div class="subfolder-view">
          <div class="subfolder-header">
            <div class="navigation-buttons">
              <button class="back-button" on:click={backToMain}>← Main</button>
              <button class="nav-button prev-button" on:click={goToPreviousVideo}>← Previous Video</button>
              <button class="nav-button next-button" on:click={goToNextVideo}>Next Video →</button>
            </div>
            <h3>Subfolder: {selectedSubfolder}</h3>
            <div class="subfolder-actions">
              {#if txtFolderSelected}
                <div class="txt-status">
                  TXT File: 
                  {#if hasTxtFile(selectedSubfolder)}
                    <span class="txt-exists">Available</span>
                    {#if getTxtFileContent(selectedSubfolder).length > 0}
                      {@const txtContent = getTxtFileContent(selectedSubfolder)}
                      <span class="txt-stats">({txtContent.length} labels)</span>
                      <button class="import-labels-btn" on:click={importTxtLabelsAsColors}>Import Labels</button>
                    {/if}
                  {:else}
                    <span class="txt-missing">Not Found</span>
                  {/if}
                </div>
              {/if}
            </div>
          </div>
          
          <!-- Labeling controls -->
          <div class="labeling-container">
            <div class="labeling-controls">
              <h3>Image Labeling</h3>
              
              <!-- Label input -->
              <div class="label-input">
                <input 
                  type="text" 
                  placeholder="Enter label name" 
                  bind:value={newLabelName}
                  on:keydown={(e) => e.key === 'Enter' && addLabel()}
                />
                <input type="color" bind:value={newLabelColor} />
                <button on:click={addLabel} class="add-label-btn">Add Label</button>
              </div>
              
              <!-- Label list -->
              {#if labels.length > 0}
                <div class="label-list">
                  {#each labels as label, i}
                    <div 
                      class="label-item" 
                      style="background-color: {label.color}; color: {getBrightness(label.color) > 128 ? 'black' : 'white'}"
                      class:active={activeLabel === label}
                      on:click={() => setActiveLabel(label)}
                      role="button"
                      tabindex="0"
                      on:keydown={(e) => e.key === 'Enter' && setActiveLabel(label)}
                    >
                      {label.name}
                      <span 
                        class="label-remove" 
                        on:click|stopPropagation={() => removeLabel(i)}
                        role="button"
                        tabindex="0"
                        on:keydown|stopPropagation={(e) => e.key === 'Enter' && removeLabel(i)}
                      >×</span>
                    </div>
                  {/each}
                </div>
                
                <div class="instructions">
                  {#if activeLabel}
                    <p>Active label: <strong>{activeLabel.name}</strong></p>
                    <p>Click images to apply this label. Shift+click to select multiple.</p>
                  {:else}
                    <p>Click a label above to activate it, then click images to apply the label.</p>
                  {/if}
                </div>
              {/if}
              
              <!-- Save Results button -->
              <button class="save-button" on:click={saveResults}>
                Save Labels to TXT
              </button>
              
              {#if txtFolderSelected && hasTxtFile(selectedSubfolder)}
                <div class="txt-file-info">
                  <h4>TXT File Analysis</h4>
                  {#if getTxtFileContent(selectedSubfolder).length > 0}
                    {@const txtContent = getTxtFileContent(selectedSubfolder)}
                    {@const uniqueLabels = [...new Set(txtContent)]}
                    
                    <div class="txt-label-stats">
                      {#each uniqueLabels as label}
                        {@const count = txtContent.filter(l => l === label).length}
                        <div class="txt-label-count">
                          <span class="txt-label-name">{label || "NIL"}</span>: 
                          <span class="txt-label-number">{count}</span>
                          <span class="txt-label-percent">({(count / txtContent.length * 100).toFixed(1)}%)</span>
                        </div>
                      {/each}
                    </div>
                  {/if}
                </div>
              {/if}
            </div>
            
            <!-- Selected images summary -->
            <div class="selected-list">
              <h3>Labeled Images:</h3>
              {#each [...new Set(Object.values(selectedImages))] as label}
                <div class="label-summary">
                  <h4>
                    <span class="color-box" style="background: {label.color}"></span>
                    {label.name}
                  </h4>
                  <p>{Object.entries(selectedImages).filter(([_, l]) => l === label).length} images</p>
                </div>
              {/each}
            </div>
          </div>
          
          <!-- Image grid -->
          <div class="image-grid">
            {#if filesDict[selectedSubfolder]}
              {#each filesDict[selectedSubfolder] as filePath, index}
                {#if getImageUrl(filePath)}
                  {@const imageUrl = getImageUrl(filePath)}
                  {@const hasNonNilLabel = selectedImages[filePath] !== undefined}
                  
                  <div 
                    class="image-item"
                    style="border: 5px solid {hasNonNilLabel ? selectedImages[filePath].color : 'transparent'}"
                    on:click={(event) => toggleSelection(filePath, event)}
                    role="button"
                    tabindex="0"
                    on:keydown={(e) => e.key === 'Enter' && toggleSelection(filePath, { shiftKey: false } as MouseEvent)}
                  >
                    <img src={imageUrl} alt={filePath.split('/')[1]} />
                    <div class="image-name">{filePath.split('/')[1]}</div>
                    
                    {#if hasNonNilLabel}
                      <div class="label-badge" style="background-color: {selectedImages[filePath].color}; color: {getBrightness(selectedImages[filePath].color) > 128 ? 'black' : 'white'}">
                        {selectedImages[filePath].name}
                      </div>
                    {/if}
                  </div>
                {/if}
              {/each}
            {/if}
          </div>
        </div>
      {/if}
    {/if}
  </main>
  
  <style>
    main {
      font-family: Arial, sans-serif;
      max-width: 1200px;
      margin: 0 auto;
      padding: 20px;
    }
    
    .input-container {
      display: flex;
      flex-direction: column;
      gap: 10px;
      margin-bottom: 20px;
    }
    
    .file-input-container {
      display: flex;
      align-items: center;
    }
    
    input[type="file"] {
      display: none;
    }
    
    .file-input-label {
      background-color: #4CAF50;
      border: none;
      color: white;
      padding: 12px 24px;
      text-align: center;
      text-decoration: none;
      display: inline-block;
      font-size: 16px;
      cursor: pointer;
      border-radius: 4px;
    }
    
    .txt-folder-label {
      background-color: #2196F3;
    }
    
    .txt-folder-label:hover {
      background-color: #0b7dda;
    }
    
    .file-input-label:hover {
      background-color: #45a049;
    }
    
    .clear-button {
      background-color: #f44336;
      border: none;
      color: white;
      padding: 12px 24px;
      text-align: center;
      text-decoration: none;
      display: inline-block;
      font-size: 16px;
      margin-left: 10px;
      cursor: pointer;
      border-radius: 4px;
    }
    
    .clear-button:hover {
      background-color: #d32f2f;
    }
    
    .file-count {
      color: #666;
      font-style: italic;
    }
    
    .subfolder-list {
      margin-top: 20px;
    }
    
    .subfolder-table {
      width: 100%;
      border-collapse: collapse;
      margin-top: 15px;
    }
    
    .subfolder-table th {
      background-color: #f2f2f2;
      padding: 12px 15px;
      text-align: left;
      border-bottom: 2px solid #ddd;
    }
    
    .subfolder-row {
      border-bottom: 1px solid #ddd;
      cursor: pointer;
      transition: background-color 0.2s;
    }
    
    .subfolder-row:hover {
      background-color: #f0f0f0;
    }
    
    .subfolder-row td {
      padding: 12px 15px;
    }
    
    .folder-name-cell {
      display: flex;
      align-items: center;
    }
    
    .folder-icon {
      font-size: 18px;
      margin-right: 10px;
    }
    
    .image-count-cell {
      text-align: center;
      color: #555;
      font-weight: 500;
    }
    
    .txt-status-cell {
      text-align: center;
    }
    
    .txt-exists {
      color: #4CAF50;
      font-weight: bold;
    }
    
    .txt-missing {
      color: #f44336;
    }
    
    .txt-stats {
      margin-left: 8px;
      font-size: 14px;
      color: #666;
    }
    
    .subfolder-view {
      margin-top: 20px;
    }
    
    .subfolder-header {
      display: flex;
      flex-direction: column;
      margin-bottom: 15px;
    }

    .navigation-buttons {
      display: flex;
      margin-bottom: 10px;
      gap: 10px;
      justify-content: flex-start;
    }

    .subfolder-header h3 {
      margin: 10px 0;
    }
    
    .back-button {
      background-color: #2196F3;
      border: none;
      color: white;
      padding: 8px 16px;
      text-align: center;
      text-decoration: none;
      display: inline-block;
      font-size: 14px;
      margin-right: 15px;
      cursor: pointer;
      border-radius: 4px;
    }
    
    .back-button:hover {
      background-color: #0b7dda;
    }

    .nav-button {
      background-color: #9C27B0;
      border: none;
      color: white;
      padding: 8px 16px;
      text-align: center;
      text-decoration: none;
      display: inline-block;
      font-size: 14px;
      margin-right: 10px;
      cursor: pointer;
      border-radius: 4px;
    }

    .nav-button:hover {
      background-color: #7B1FA2;
    }

    /* Button spacing handled by flex container */
    
    .txt-status {
      margin-left: 20px;
      padding: 6px 12px;
      background-color: #f5f5f5;
      border-radius: 4px;
      border: 1px solid #ddd;
    }
    
    .import-labels-btn {
      margin-left: 10px;
      padding: 4px 8px;
      background-color: #673AB7;
      color: white;
      border: none;
      border-radius: 4px;
      cursor: pointer;
      font-size: 12px;
    }
    
    .import-labels-btn:hover {
      background-color: #5E35B1;
    }
    
    .image-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
      gap: 15px;
      margin-top: 20px;
    }
    
    .image-item {
      background-color: #f9f9f9;
      border-radius: 8px;
      padding: 5px;
      transition: transform 0.1s;
      display: flex;
      flex-direction: column;
      cursor: pointer;
    }
    
    .image-item:hover {
      transform: translateY(-2px);
      box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    
    .image-item img {
      width: 100%;
      height: 150px;
      object-fit: contain;
      border-radius: 3px;
      background-color: #f0f0f0;
    }
    
    .image-name {
      margin-top: 8px;
      font-size: 12px;
      text-align: center;
      word-break: break-word;
      color: #555;
    }
    
    .label-badge {
      margin-top: 4px;
      padding: 3px 6px;
      border-radius: 12px;
      font-size: 11px;
      text-align: center;
      font-weight: bold;
      align-self: center;
    }
  
    /* Labeling styles */
    .labeling-container {
      display: flex;
      margin-top: 20px;
      border: 1px solid #ddd;
      padding: 15px;
      border-radius: 8px;
      background-color: #f5f5f5;
    }
    
    .labeling-controls {
      flex: 2;
      margin-right: 20px;
    }
    
    .selected-list {
      flex: 1;
      border-left: 1px solid #ddd;
      padding-left: 20px;
    }
    
    .label-input {
      display: flex;
      gap: 10px;
      margin-bottom: 15px;
    }
    
    .label-input input[type="text"] {
      flex-grow: 1;
      padding: 8px;
      border-radius: 4px;
      border: 1px solid #ccc;
    }
    
    .add-label-btn {
      padding: 8px 12px;
      background-color: #4CAF50;
      color: white;
      border: none;
      border-radius: 4px;
      cursor: pointer;
    }
    
    .add-label-btn:hover {
      background-color: #45a049;
    }
    
    .label-list {
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      margin-bottom: 15px;
    }
    
    .label-item {
      display: flex;
      align-items: center;
      padding: 8px 12px;
      border-radius: 20px;
      cursor: pointer;
      user-select: none;
    }
    
    .label-item.active {
      outline: 3px solid black;
    }
    
    .label-remove {
      margin-left: 8px;
      cursor: pointer;
      font-weight: bold;
    }
    
    .instructions {
      margin-bottom: 15px;
      font-size: 14px;
      color: #666;
    }
    
    .save-button {
      padding: 10px 15px;
      background-color: #007BFF;
      color: white;
      border: none;
      border-radius: 4px;
      cursor: pointer;
      font-size: 16px;
      display: flex;
      align-items: center;
      gap: 5px;
    }
    
    .save-button:hover {
      background-color: #0056b3;
    }
    
    .save-button::before {
      content: "💾";
    }
    
    .color-box {
      width: 20px;
      height: 20px;
      display: inline-block;
      margin-right: 5px;
      border-radius: 4px;
    }
    
    .label-summary {
      margin-bottom: 10px;
    }
    
    .label-summary h4 {
      margin: 0 0 5px 0;
      display: flex;
      align-items: center;
    }
    
    .txt-file-info {
      margin-top: 20px;
      padding: 15px;
      background-color: #fff;
      border-radius: 6px;
      border: 1px solid #ddd;
    }
    
    .txt-file-info h4 {
      margin-top: 0;
      margin-bottom: 10px;
      padding-bottom: 5px;
      border-bottom: 1px solid #eee;
    }
    
    .txt-label-stats {
      display: flex;
      flex-direction: column;
      gap: 5px;
    }
    
    .txt-label-count {
      font-size: 14px;
    }
    
    .txt-label-name {
      font-weight: bold;
    }
    
    .txt-label-number {
      color: #2196F3;
    }
    
    .txt-label-percent {
      color: #666;
      margin-left: 5px;
    }
    
    .unique-labels-container {
      margin-top: 10px;
      padding: 12px;
      background-color: #f9f9f9;
      border: 1px solid #ddd;
      border-radius: 4px;
    }
    
    .unique-labels-container h4 {
      margin-top: 0;
      margin-bottom: 10px;
      font-size: 14px;
      color: #555;
    }
    
    .unique-labels-list {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
    }
    
    .unique-label-item {
      padding: 4px 8px;
      background-color: #e3f2fd;
      color: #0d47a1;
      border-radius: 12px;
      font-size: 12px;
      font-weight: 500;
      border: 1px solid #bbdefb;
    }
    
    .subfolder-actions {
      display: flex;
      align-items: center;
      gap: 15px;
    }
    
    /* Loading spinner animation */
    @keyframes spin {
      0% { transform: rotate(0deg); }
      100% { transform: rotate(360deg); }
    }
    
    .loading-spinner {
      display: inline-block;
      width: 16px;
      height: 16px;
      border: 3px solid rgba(255,255,255,0.3);
      border-radius: 50%;
      border-top-color: #fff;
      animation: spin 1s ease-in-out infinite;
      margin-right: 8px;
    }
  </style>