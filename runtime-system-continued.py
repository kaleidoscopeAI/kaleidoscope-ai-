.running = False
        self.logger.info("Shutting down runtime manager...")
        self._cleanup()
        sys.exit(0)

    async def start(self):
        self.running = True
        self.logger.info("Starting runtime manager...")
        
        # Initialize ZMQ sockets
        self.market_socket = self.context.socket(zmq.SUB)
        self.molecule_socket = self.context.socket(zmq.SUB)
        self.sensor_socket = self.context.socket(zmq.SUB)
        self.output_socket = self.context.socket(zmq.PUB)
        
        self.market_socket.bind("tcp://*:5555")
        self.molecule_socket.bind("tcp://*:5556")
        self.sensor_socket.bind("tcp://*:5557")
        self.output_socket.bind("tcp://*:5558")
        
        # Start worker processes
        for _ in range(self.config.num_workers):
            worker = mp.Process(target=self._worker_process)
            worker.start()
            self.workers.append(worker)
            
        # Start async tasks
        tasks = [
            self._market_consumer(),
            self._molecule_consumer(),
            self._sensor_consumer(),
            self._model_inference(),
            self._security_monitor()
        ]
        
        await asyncio.gather(*tasks)
        
    async def _market_consumer(self):
        while self.running:
            try:
                msg = await self.market_socket.recv_multipart()
                data = msgpack.unpackb(msg[1], raw=False)
                await self.market_queue.put(torch.tensor(data['market_data']))
            except Exception as e:
                self.logger.error(f"Market consumer error: {e}")
                await asyncio.sleep(0.1)

    async def _molecule_consumer(self):
        while self.running:
            try:
                msg = await self.molecule_socket.recv_multipart()
                data = msgpack.unpackb(msg[1], raw=False)
                await self.molecule_queue.put(torch.tensor(data['molecule_data']))
            except Exception as e:
                self.logger.error(f"Molecule consumer error: {e}")
                await asyncio.sleep(0.1)

    async def _sensor_consumer(self):
        while self.running:
            try:
                msg = await self.sensor_socket.recv_multipart()
                data = msgpack.unpackb(msg[1], raw=False)
                await self.sensor_queue.put(torch.tensor(data['sensor_data']))
            except Exception as e:
                self.logger.error(f"Sensor consumer error: {e}")
                await asyncio.sleep(0.1)

    async def _model_inference(self):
        while self.running:
            try:
                # Gather batch data
                market_batch = []
                molecule_batch = []
                sensor_batch = []
                
                while (len(market_batch) < self.config.batch_size and
                       not self.market_queue.empty()):
                    market_batch.append(await self.market_queue.get())
                    
                while (len(molecule_batch) < self.config.batch_size and
                       not self.molecule_queue.empty()):
                    molecule_batch.append(await self.molecule_queue.get())
                    
                while (len(sensor_batch) < self.config.batch_size and
                       not self.sensor_queue.empty()):
                    sensor_batch.append(await self.sensor_queue.get())
                
                if market_batch and molecule_batch and sensor_batch:
                    # Prepare batch tensors
                    market_tensor = torch.stack(market_batch).to(self.device)
                    molecule_tensor = torch.stack(molecule_batch).to(self.device)
                    sensor_tensor = torch.stack(sensor_batch).to(self.device)
                    
                    # Security check
                    security_status = self.security_system.process_data(
                        market_tensor, molecule_tensor, sensor_tensor
                    )
                    
                    if security_status['threat_level'] < 2:
                        with torch.no_grad():
                            # Model inference
                            market_pred, molecule_pred, sensor_pred, uncertainties = \
                                self.model(market_tensor, molecule_tensor, sensor_tensor)
                            
                            # Prepare output
                            output = {
                                'market_predictions': market_pred.cpu().numpy(),
                                'molecule_predictions': molecule_pred.cpu().numpy(),
                                'sensor_predictions': sensor_pred.cpu().numpy(),
                                'uncertainties': uncertainties.cpu().numpy(),
                                'security_status': security_status,
                                'timestamp': time.time()
                            }
                            
                            # Send output
                            await self.output_socket.send_multipart([
                                b'predictions',
                                msgpack.packb(output, default=m.encode)
                            ])
                    else:
                        self.logger.warning(f"High threat level detected: {security_status}")
                        
            except Exception as e:
                self.logger.error(f"Model inference error: {e}")
                await asyncio.sleep(0.1)

    async def _security_monitor(self):
        while self.running:
            try:
                # Check system status
                security_metrics = self.security_system.get_security_state()
                
                # Log security status
                if security_metrics['threat_level'] > 1:
                    self.logger.warning(f"Security alert: {security_metrics}")
                    
                # Send security update
                await self.output_socket.send_multipart([
                    b'security',
                    msgpack.packb(security_metrics, default=m.encode)
                ])
                
                await asyncio.sleep(self.config.update_interval)
                
            except Exception as e:
                self.logger.error(f"Security monitor error: {e}")
                await asyncio.sleep(1.0)

    def _worker_process(self):
        try:
            while self.running:
                # Process queued data
                if not self.market_queue.empty():
                    market_data = self.market_queue.get()
                    self._process_market_data(market_data)
                    
                if not self.molecule_queue.empty():
                    molecule_data = self.molecule_queue.get()
                    self._process_molecule_data(molecule_data)
                    
                if not self.sensor_queue.empty():
                    sensor_data = self.sensor_queue.get()
                    self._process_sensor_data(sensor_data)
                    
                time.sleep(0.001)  # Prevent CPU thrashing
                
        except Exception as e:
            self.logger.error(f"Worker process error: {e}")

    def _process_market_data(self, data: torch.Tensor):
        try:
            # Market-specific preprocessing
            processed = self._preprocess_market_data(data)
            self.market_queue.put(processed)
        except Exception as e:
            self.logger.error(f"Market processing error: {e}")

    def _process_molecule_data(self, data: torch.Tensor):
        try:
            # Molecule-specific preprocessing
            processed = self._preprocess_molecule_data(data)
            self.molecule_queue.put(processed)
        except Exception as e:
            self.logger.error(f"Molecule processing error: {e}")

    def _process_sensor_data(self, data: torch.Tensor):
        try:
            # Sensor-specific preprocessing
            processed = self._preprocess_sensor_data(data)
            self.sensor_queue.put(processed)
        except Exception as e:
            self.logger.error(f"Sensor processing error: {e}")

    def _preprocess_market_data(self, data: torch.Tensor) -> torch.Tensor:
        # Apply market-specific normalization and feature extraction
        normalized = (data - data.mean()) / (data.std() + 1e-8)
        features = self._extract_market_features(normalized)
        return features

    def _preprocess_molecule_data(self, data: torch.Tensor) -> torch.Tensor:
        # Apply molecule-specific normalization and feature extraction
        normalized = (data - data.mean()) / (data.std() + 1e-8)
        features = self._extract_molecule_features(normalized)
        return features

    def _preprocess_sensor_data(self, data: torch.Tensor) -> torch.Tensor:
        # Apply sensor-specific normalization and feature extraction
        normalized = (data - data.mean()) / (data.std() + 1e-8)
        features = self._extract_sensor_features(normalized)
        return features

    def _extract_market_features(self, data: torch.Tensor) -> torch.Tensor:
        # Extract relevant market features
        features = torch.cat([
            data,
            torch.diff(data, dim=-1, prepend=data[..., :1]),
            torch.roll(data, shifts=1, dims=-1) - data
        ], dim=-1)
        return features

    def _extract_molecule_features(self, data: torch.Tensor) -> torch.Tensor:
        # Extract relevant molecule features
        features = torch.cat([
            data,
            torch.mean(data, dim=-1, keepdim=True),
            torch.std(data, dim=-1, keepdim=True)
        ], dim=-1)
        return features

    def _extract_sensor_features(self, data: torch.Tensor) -> torch.Tensor:
        # Extract relevant sensor features
        features = torch.cat([
            data,
            torch.gradient(data)[0],
            torch.gradient(torch.gradient(data)[0])[0]
        ], dim=-1)
        return features

    def _cleanup(self):
        # Stop all workers
        for worker in self.workers:
            worker.terminate()
            worker.join()
            
        # Close ZMQ sockets
        self.market_socket.close()
        self.molecule_socket.close()
        self.sensor_socket.close()
        self.output_socket.close()
        
        # Close queues
        self.market_queue.close()
        self.molecule_queue.close()
        self.sensor_queue.close()
        
        self.context.term()
        self.logger.info("Runtime manager cleanup complete")

