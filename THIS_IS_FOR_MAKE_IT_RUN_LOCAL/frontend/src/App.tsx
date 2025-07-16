import React, { useState, useCallback } from 'react';
import axios from 'axios';
import {
  LiveKitRoom,
  VideoConference,
  formatChatMessageLinks,
} from '@livekit/components-react';
import '@livekit/components-styles';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

interface TokenResponse {
  token: string;
  room_name: string;
  ws_url: string;
}

function App() {
  const [token, setToken] = useState<string>('');
  const [wsUrl, setWsUrl] = useState<string>('');
  const [roomName, setRoomName] = useState<string>('');
  const [participantName, setParticipantName] = useState<string>('');
  const [customRoomName, setCustomRoomName] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string>('');
  const [connected, setConnected] = useState<boolean>(false);

  const joinRoom = useCallback(async () => {
    if (!participantName.trim()) {
      setError('Please enter your name');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const response = await axios.post<TokenResponse>(`${API_BASE_URL}/create-room-and-token`, {
        participant_name: participantName.trim(),
        room_name: customRoomName.trim() || undefined,
      });

      const { token, room_name, ws_url } = response.data;
      setToken(token);
      setRoomName(room_name);
      setWsUrl(ws_url);
      setConnected(true);
      console.log('✅ Successfully joined room:', room_name);
    } catch (err: any) {    
      console.error('Failed to join room:', err);
      setError(
        err.response?.data?.detail || 
        'Failed to join room. Please check if the backend is running.'
      );
    } finally {
      setLoading(false);
    }
  }, [participantName, customRoomName]);

  const leaveRoom = useCallback(() => {
    setToken('');
    setWsUrl('');
    setRoomName('');
    setConnected(false);
    setError('');
  }, []);

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      joinRoom();
    }
  };

  if (connected && token && wsUrl) {
    return (
      <div style={{ height: '100vh', width: '100vw' }}>
        <button className="leave-button" onClick={leaveRoom}>
          Leave Room
        </button>
        <LiveKitRoom
          video={true}
          audio={true}
          token={token}
          serverUrl={wsUrl}
          data-lk-theme="default"
          style={{ height: '100vh' }}
          onDisconnected={leaveRoom}
        >
          <VideoConference 
            chatMessageFormatter={formatChatMessageLinks}
          />
        </LiveKitRoom>
      </div>
    );
  }

  return (
    <div>
      <h1>🎥 LiveKit RAG Agent</h1>
      <p>Join a video conference with AI-powered document assistance</p>
      
      <div className="join-form">
        <h2>Join Video Room</h2>
        
        {error && (
          <div className="error">
            {error}
          </div>
        )}
        
        <div className="form-group">
          <label htmlFor="participantName">Your Name *</label>
          <input
            id="participantName"
            type="text"
            value={participantName}
            onChange={(e) => setParticipantName(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Enter your name"
            disabled={loading}
          />
        </div>
        
        <div className="form-group">
          <label htmlFor="roomName">Room Name (optional)</label>
          <input
            id="roomName"
            type="text"
            value={customRoomName}
            onChange={(e) => setCustomRoomName(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Leave empty for auto-generated room"
            disabled={loading}
          />
        </div>
        
        <button 
          className="join-button"
          onClick={joinRoom}
          disabled={loading || !participantName.trim()}
        >
          {loading ? 'Joining...' : 'Join Room'}
        </button>
      </div>

      <div className="card">
        <h3>🤖 AI Assistant Features</h3>
        <div className="features-grid">
          <div className="feature-item">
            <span className="feature-icon">🎥</span>
            <div>
              <strong>HD Video Conference</strong>
              <p>High-quality video calls with multiple participants</p>
            </div>
          </div>
          <div className="feature-item">
            <span className="feature-icon">🤖</span>
            <div>
              <strong>AI Document Assistant</strong>
              <p>Ask questions about ML, AI, and Deep Learning topics</p>
            </div>
          </div>
          <div className="feature-item">
            <span className="feature-icon">💬</span>
            <div>
              <strong>Voice & Chat</strong>
              <p>Real-time communication with AI responses</p>
            </div>
          </div>
        </div>
      </div>

      <div className="card">
        <h3>📚 Available Knowledge Base</h3>
        <ul style={{ textAlign: 'left', maxWidth: '500px', margin: '0 auto' }}>
          <li><strong>Machine Learning Fundamentals</strong> - Core ML concepts and algorithms</li>
          <li><strong>Deep Learning</strong> - Neural networks, architectures, and training</li>
          <li><strong>AI Research Papers</strong> - Latest developments and methodologies</li>
        </ul>
      </div>

      <div className="card">
        <h3>🎙️ How to Use the AI Assistant</h3>
        <div className="instructions">
          <ol style={{ textAlign: 'left', maxWidth: '700px', margin: '10 auto' }}>
            <li><strong>Join the room</strong> - Enter your name and click "Join Room"</li>
            <li><strong>Wait for AI greeting</strong> - The AI assistant will introduce itself</li>
            <li><strong>Ask questions</strong> - Speak or type questions about the documents</li>
            <li><strong>Get answers</strong> - Receive detailed responses from the knowledge base</li>
          </ol>
          <div className="example-questions"> 
            <h4>💡 Example Questions:</h4>
            <ul>
              <li>"What is machine learning?"</li>
              <li>"Explain neural networks"</li>
              <li>"How does deep learning work?"</li>
              <li>"What are the types of machine learning?"</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
