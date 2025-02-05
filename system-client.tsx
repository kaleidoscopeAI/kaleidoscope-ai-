import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from 'recharts';
import { Terminal, MessageSquare, Database, Activity } from 'lucide-react';

const SystemInterface = () => {
  const [messages, setMessages] = useState([]);
  const [systemMetrics, setSystemMetrics] = useState([]);
  const [wsConnection, setWsConnection] = useState(null);
  const [activeTab, setActiveTab] = useState('chat');

  useEffect(() => {
    // Connect to WebSocket
    const ws = new WebSocket('ws://localhost:8765');
    
    ws.onopen = () => {
      console.log('Connected to system');
      setWsConnection(ws);
    };
    
    ws.onmessage = (event) => {
      const response = JSON.parse(event.data);
      handleSystemResponse(response);
    };
    
    return () => ws.close();
  }, []);

  const handleSystemResponse = (response) => {
    if (response.type === 'metrics') {
      setSystemMetrics(prev => [...prev, response.data]);
    } else {
      setMessages(prev => [...prev, { 
        type: 'response', 
        content: response.response 
      }]);
    }
  };

  const sendQuery = (text) => {
    if (wsConnection) {
      wsConnection.send(JSON.stringify({
        query_text: text,
        query_type: 'general'
      }));
      
      setMessages(prev => [...prev, { 
        type: 'query', 
        content: text 
      }]);
    }
  };

  return (
    <div className="min-h-screen bg-gray-100">
      <div className="container mx-auto p-6">
        {/* Header */}
        <div className="mb-8 flex justify-between items-center">
          <h1 className="text-3xl font-bold text-gray-800">
            Quantum System Interface
          </h1>
          <div className="flex space-x-4">
            <button
              onClick={() => setActiveTab('chat')}
              className={`px-4 py-2 rounded ${
                activeTab === 'chat' ? 'bg-blue-500 text-white' : 'bg-white'
              }`}
            >
              <MessageSquare className="w-5 h-5" />
            </button>
            <button
              onClick={() => setActiveTab('metrics')}
              className={`px-4 py-2 rounded ${
                activeTab === 'metrics' ? 'bg-blue-500 text-white' : 'bg-white'
              }`}
            >
              <Activity className="w-5 h-5" />
            </button>
            <button
              onClick={() => setActiveTab('data')}
              className={`px-4 py-2 rounded ${
                activeTab === 'data' ? 'bg-blue-500 text-white' : 'bg-white'
              }`}
            >
              <Database className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Main Content */}
        <div className="grid grid-cols-3 gap-6">
          {/* Chat Interface */}
          <div className="col-span-2 bg-white rounded-lg shadow-lg p-6">
            <div className="h-96 overflow-y-auto mb-4 space-y-4">
              {messages.map((msg, idx) => (
                <div
                  key={idx}
                  className={`p-3 rounded-lg ${
                    msg.type === 'query' 
                      ? 'bg-blue-100 ml-12' 
                      : 'bg-gray-100 mr-12'
                  }`}
                >
                  {msg.content}
                </div>
              ))}
            </div>
            
            <div className="flex space-x-2">
              <input
                type="text"
                placeholder="Enter your query..."
                className="flex-1 p-2 border rounded"
                onKeyPress={(e) => {
                  if (e.key === 'Enter') {
                    sendQuery(e.target.value);
                    e.target.value = '';
                  }
                }}
              />
              <button 
                className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
              >
                Send
              </button>
            </div>
          </div>

          {/* System Metrics */}
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h2 className="text-xl font-semibold mb-4">System Metrics</h2>
            <LineChart width={400} height={300} data={systemMetrics}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="timestamp" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line 
                type="monotone" 
                dataKey="processing" 
                stroke="#8884d8" 
              />
              <Line 
                type="monotone" 
                dataKey="memory" 
                stroke="#82ca9d" 
              />
            </LineChart>
            
            <div className="mt-4 space-y-2">
              <div className="flex justify-between items-center p-2 bg-gray-50 rounded">
                <span>System Status</span>
                <span className="px-2 py-1 bg-green-100 text-green-800 rounded">
                  Active
                </span>
              </div>
              <div className="flex justify-between items-center p-2 bg-gray-50 rounded">
                <span>Processing Load</span>
                <span className="px-2 py-1 bg-blue-100 text-blue-800 rounded">
                  {systemMetrics[systemMetrics.length - 1]?.processing || 0}%
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SystemInterface;
