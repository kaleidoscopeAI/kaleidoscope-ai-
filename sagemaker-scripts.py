# membrane_processor.py
import torch
import numpy as np
from pathlib import Path
import json

def process():
    input_path = Path('/opt/ml/processing/input')
    output_path = Path('/opt/ml/processing/output')
    output_path.mkdir(exist_ok=True)
    
    # Load data
    data = np.load(input_path / 'data.npy')
    
    # Calculate optimal chunks
    chunk_size = 1024 * 1024  # 1MB
    num_chunks = max(1, data.size // chunk_size)
    
    chunks = np.array_split(data, num_chunks)
    
    # Save chunks
    for i, chunk in enumerate(chunks):
        np.save(output_path / f'chunk_{i}.npy', chunk)
        
    # Save metadata
    with open(output_path / 'metadata.json', 'w') as f:
        json.dump({
            'num_chunks': num_chunks,
            'chunk_size': chunk_size,
            'total_size': data.size
        }, f)

if __name__ == '__main__':
    process()

# node_processor.py
import torch
import torch.nn as nn
import numpy as np
from pathlib import Path
import json

class NodeNetwork(nn.Module):
    def __init__(self, input_size):
        super().__init__()
        self.network = nn.Sequential(
            nn.Linear(input_size, 512),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(512, 256),
            nn.ReLU(),
            nn.Linear(256, 64)
        )
        
    def forward(self, x):
        return self.network(x)

def process():
    input_path = Path('/opt/ml/processing/input')
    output_path = Path('/opt/ml/processing/output')
    output_path.mkdir(exist_ok=True)
    
    # Load metadata
    with open(input_path / 'metadata.json', 'r') as f:
        metadata = json.load(f)
        
    # Process each chunk
    results = []
    for i in range(metadata['num_chunks']):
        chunk = np.load(input_path / f'chunk_{i}.npy')
        tensor = torch.from_numpy(chunk).float()
        
        # Create and process through network
        network = NodeNetwork(chunk.shape[1])
        if torch.cuda.is_available():
            network = network.cuda()
            tensor = tensor.cuda()
            
        with torch.no_grad():
            processed = network(tensor)
            results.append(processed.cpu().numpy())
            
    # Save results
    np.save(output_path / 'processed_data.npy', np.concatenate(results))
    
if __name__ == '__main__':
    process()

# engine_training.py
import os
import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
from pathlib import Path

class KaleidoscopeEngine(nn.Module):
    def __init__(self, input_dim=64):
        super().__init__()
        self.encoder = nn.Sequential(
            nn.Linear(input_dim, 128),
            nn.ReLU(),
            nn.Linear(128, 256),
            nn.ReLU(),
            nn.Linear(256, 512)
        )
        
        self.decoder = nn.Sequential(
            nn.Linear(512, 256),
            nn.ReLU(),
            nn.Linear(256, 128),
            nn.ReLU(),
            nn.Linear(128, input_dim)
        )
        
    def forward(self, x):
        encoded = self.encoder(x)
        decoded = self.decoder(encoded)
        return decoded, encoded

def train(args):
    # Training setup
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model = KaleidoscopeEngine().to(device)
    optimizer = optim.Adam(model.parameters(), lr=args.learning_rate)
    criterion = nn.MSELoss()
    
    # Load data
    train_data = np.load(os.path.join(args.train, 'processed_data.npy'))
    train_tensor = torch.from_numpy(train_data).float().to(device)
    
    # Training loop
    for epoch in range(args.epochs):
        total_loss = 0
        for i in range(0, len(train_tensor), args.batch_size):
            batch = train_tensor[i:i+args.batch_size]
            
            optimizer.zero_grad()
            reconstructed, encoded = model(batch)
            loss = criterion(reconstructed, batch)
            loss.backward()
            optimizer.step()
            
            total_loss += loss.item()
            
        print(f'Epoch {epoch}: Loss = {total_loss/len(train_tensor)}')
    
    # Save model
    torch.save(model.state_dict(), os.path.join(args.model_dir, 'model.pt'))

def model_fn(model_dir):
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model = KaleidoscopeEngine()
    model.load_state_dict(torch.load(os.path.join(model_dir, 'model.pt')))
    return model.to(device)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    
    parser.add_argument('--train', type=str, default=os.environ.get('SM_CHANNEL_TRAIN'))
    parser.add_argument('--model-dir', type=str, default=os.environ.get('SM_MODEL_DIR'))
    parser.add_argument('--epochs', type=int, default=50)
    parser.add_argument('--batch-size', type=int, default=128)
    parser.add_argument('--learning-rate', type=float, default=0.001)
    
    args = parser.parse_args()
    train(args)
