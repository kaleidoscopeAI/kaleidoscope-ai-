novelty(pattern_hash)
            
    def _hash_pattern(
        self,
        market_pattern: List[float],
        molecule_pattern: List[float],
        sensor_pattern: List[float]
    ) -> str:
        combined = np.concatenate([market_pattern, molecule_pattern, sensor_pattern])
        discretized = np.floor(combined * 100).astype(int)
        return hashlib.sha256(discretized.tobytes()).hexdigest()
    
    def _update_pattern_graph(self, current_hash: str):
        for prev_hash in self.pattern_counts:
            if prev_hash != current_hash:
                weight = self.pattern_counts[prev_hash] / sum(self.pattern_counts.values())
                self.pattern_graph.add_edge(prev_hash, current_hash, weight=weight)
    
    def _calculate_pattern_novelty(self, pattern_hash: str) -> float:
        if len(self.pattern_counts) < 2:
            return 1.0
            
        pattern_dist = [count / sum(self.pattern_counts.values()) 
                       for count in self.pattern_counts.values()]
        base_entropy = entropy(pattern_dist)
        
        if pattern_hash in self.pattern_graph:
            node_centrality = nx.pagerank(self.pattern_graph)[pattern_hash]
            return 1.0 - node_centrality
        return 1.0

class ThreatDetector:
    def __init__(
        self,
        hidden_dim: int = 256,
        num_heads: int = 8,
        num_layers: int = 4
    ):
        self.hidden_dim = hidden_dim
        self.threat_encoder = nn.TransformerEncoder(
            nn.TransformerEncoderLayer(
                d_model=hidden_dim,
                nhead=num_heads,
                dim_feedforward=4*hidden_dim,
                dropout=0.1,
                batch_first=True
            ),
            num_layers=num_layers
        )
        
        self.threat_classifier = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim),
            nn.LayerNorm(hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, 3)  # Three threat levels
        )
        
        self.domain_embedding = nn.Linear(hidden_dim, hidden_dim)
        self.threat_memory = deque(maxlen=10000)
        
    def detect_threats(
        self,
        market_state: torch.Tensor,
        molecule_state: torch.Tensor,
        sensor_state: torch.Tensor,
        anomalies: Dict[str, List[int]]
    ) -> Dict[str, float]:
        # Embed domain states
        market_emb = self.domain_embedding(market_state)
        molecule_emb = self.domain_embedding(molecule_state)
        sensor_emb = self.domain_embedding(sensor_state)
        
        # Combine embeddings with anomaly information
        combined = torch.cat([
            market_emb,
            molecule_emb,
            sensor_emb
        ], dim=-1)
        
        # Add anomaly markers
        anomaly_tensor = torch.zeros_like(combined)
        for domain, indices in anomalies.items():
            if domain == 'market':
                anomaly_tensor[:, :self.hidden_dim][indices] = 1
            elif domain == 'molecule':
                anomaly_tensor[:, self.hidden_dim:2*self.hidden_dim][indices] = 1
            else:
                anomaly_tensor[:, 2*self.hidden_dim:][indices] = 1
        
        combined = torch.cat([combined, anomaly_tensor], dim=-1)
        
        # Encode and classify threats
        encoded = self.threat_encoder(combined)
        threat_scores = F.softmax(self.threat_classifier(encoded), dim=-1)
        
        # Update threat memory
        self.threat_memory.append({
            'timestamp': time.time(),
            'scores': threat_scores.detach().cpu().numpy()
        })
        
        return {
            'low': float(threat_scores[0]),
            'medium': float(threat_scores[1]),
            'high': float(threat_scores[2])
        }

class IntegratedSecuritySystem:
    def __init__(self):
        self.security_layer = SecurityLayer()
        self.message_queue = queue.Queue()
        self.threat_level = 0
        self.active = True
        self._start_monitoring()
        
    def _start_monitoring(self):
        self.monitor_thread = threading.Thread(target=self._security_monitor_loop)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
        
    def _security_monitor_loop(self):
        while self.active:
            try:
                message = self.message_queue.get(timeout=1.0)
                self._process_security_message(message)
            except queue.Empty:
                continue
            except Exception as e:
                print(f"Security monitor error: {e}")
                
    def _process_security_message(self, message: Dict):
        if message['type'] == 'anomaly':
            self._handle_anomaly(message['data'])
        elif message['type'] == 'threat':
            self._handle_threat(message['data'])
        elif message['type'] == 'pattern':
            self._handle_pattern(message['data'])
            
    def _handle_anomaly(self, anomaly_data: Dict):
        if anomaly_data['score'] > 0.8:
            self.threat_level = min(self.threat_level + 1, 3)
            self._trigger_security_response()
            
    def _handle_threat(self, threat_data: Dict):
        if threat_data['high'] > 0.7:
            self.threat_level = 3
            self._trigger_security_response()
        elif threat_data['medium'] > 0.7:
            self.threat_level = 2
            
    def _handle_pattern(self, pattern_data: Dict):
        if pattern_data['novelty'] > 0.9:
            self._investigate_pattern(pattern_data)
            
    def _trigger_security_response(self):
        response = {
            'timestamp': time.time(),
            'threat_level': self.threat_level,
            'action': self._determine_security_action()
        }
        self.message_queue.put({'type': 'response', 'data': response})
        
    def _determine_security_action(self) -> str:
        if self.threat_level == 3:
            return 'lockdown'
        elif self.threat_level == 2:
            return 'restrict'
        return 'monitor'
        
    def _investigate_pattern(self, pattern_data: Dict):
        investigation = {
            'timestamp': time.time(),
            'pattern_hash': pattern_data['hash'],
            'correlation_analysis': self._analyze_pattern_correlations(pattern_data)
        }
        self.message_queue.put({'type': 'investigation', 'data': investigation})
        
    def _analyze_pattern_correlations(self, pattern_data: Dict) -> Dict:
        return {
            'market_correlation': np.corrcoef(pattern_data['market'])[0, 1],
            'molecule_correlation': np.corrcoef(pattern_data['molecule'])[0, 1],
            'sensor_correlation': np.corrcoef(pattern_data['sensor'])[0, 1]
        }
        
    def process_data(
        self,
        market_data: torch.Tensor,
        molecule_data: torch.Tensor,
        sensor_data: torch.Tensor
    ) -> Dict:
        # Detect anomalies
        anomalies = self.security_layer.anomaly_detector.detect_anomalies(
            market_data, molecule_data, sensor_data
        )
        
        # Monitor patterns
        pattern_score = self.security_layer.pattern_monitor.update_patterns(
            market_data.detach().cpu().numpy(),
            molecule_data.detach().cpu().numpy(),
            sensor_data.detach().cpu().numpy()
        )
        
        # Detect threats
        threats = self.security_layer.threat_detector.detect_threats(
            market_data, molecule_data, sensor_data, anomalies
        )
        
        self.message_queue.put({
            'type': 'analysis',
            'data': {
                'anomalies': anomalies,
                'pattern_score': pattern_score,
                'threats': threats
            }
        })
        
        return {
            'anomalies': anomalies,
            'pattern_score': pattern_score,
            'threats': threats,
            'threat_level': self.threat_level
        }
        
    def shutdown(self):
        self.active = False
        self.monitor_thread.join()
