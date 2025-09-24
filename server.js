const express = require('express');
const cors = require('cors');
const path = require('path');
require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.static('.'));

// API endpoint to generate image
app.post('/api/generate', async (req, res) => {
    try {
        const { image_url, prompt, num_inference_steps, guidance_scale, num_images, enable_safety_checker, output_format, acceleration, resolution_mode, loras } = req.body;

        const response = await fetch('https://queue.fal.run/fal-ai/flux-kontext-lora', {
            method: 'POST',
            headers: {
                'Authorization': `Key ${process.env.FAL_API_KEY}`,
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                image_url,
                prompt,
                num_inference_steps,
                guidance_scale,
                num_images,
                enable_safety_checker,
                output_format,
                acceleration,
                resolution_mode,
                loras
            })
        });

        if (!response.ok) {
            throw new Error(`FAL API error: ${response.status} ${response.statusText}`);
        }

        const data = await response.json();
        res.json(data);
    } catch (error) {
        console.error('Error calling FAL API:', error);
        res.status(500).json({ error: error.message });
    }
});

// API endpoint to check status
app.get('/api/status/:requestId', async (req, res) => {
    try {
        const { requestId } = req.params;
        
        const response = await fetch(`https://queue.fal.run/fal-ai/flux-kontext-lora/requests/${requestId}/status`, {
            headers: {
                'Authorization': `Key ${process.env.FAL_API_KEY}`,
            }
        });

        if (!response.ok) {
            throw new Error(`FAL API error: ${response.status} ${response.statusText}`);
        }

        const data = await response.json();
        res.json(data);
    } catch (error) {
        console.error('Error checking status:', error);
        res.status(500).json({ error: error.message });
    }
});

// API endpoint to get result
app.get('/api/result/:requestId', async (req, res) => {
    try {
        const { requestId } = req.params;
        
        const response = await fetch(`https://queue.fal.run/fal-ai/flux-kontext-lora/requests/${requestId}`, {
            headers: {
                'Authorization': `Key ${process.env.FAL_API_KEY}`,
            }
        });

        if (!response.ok) {
            throw new Error(`FAL API error: ${response.status} ${response.statusText}`);
        }

        const data = await response.json();
        res.json(data);
    } catch (error) {
        console.error('Error getting result:', error);
        res.status(500).json({ error: error.message });
    }
});

// Serve the main HTML file
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'index.html'));
});

app.listen(PORT, () => {
    console.log(`Server running on http://localhost:${PORT}`);
    console.log('Make sure to set your FAL_API_KEY in the .env file');
});
