"""
Chunk system for infinite world generation
"""
import numpy as np


class Chunk:
    """Represents a 16x256x16 chunk of blocks"""
    
    CHUNK_SIZE = 16
    CHUNK_HEIGHT = 256
    
    def __init__(self, chunk_x, chunk_z):
        self.chunk_x = chunk_x
        self.chunk_z = chunk_z
        self.blocks = np.zeros((self.CHUNK_HEIGHT, self.CHUNK_SIZE, self.CHUNK_SIZE), dtype=np.int8)
        self.height_map = np.zeros((self.CHUNK_SIZE, self.CHUNK_SIZE), dtype=np.int16)
        self.is_generated = False
        self.is_modified = False
        
    def get_block(self, x, y, z):
        """Get block at local coordinates"""
        if 0 <= x < self.CHUNK_SIZE and 0 <= y < self.CHUNK_HEIGHT and 0 <= z < self.CHUNK_SIZE:
            return self.blocks[y, x, z]
        return 0
    
    def set_block(self, x, y, z, block_id):
        """Set block at local coordinates"""
        if 0 <= x < self.CHUNK_SIZE and 0 <= y < self.CHUNK_HEIGHT and 0 <= z < self.CHUNK_SIZE:
            self.blocks[y, x, z] = block_id
            self.is_modified = True
            
    def get_world_x(self):
        """Get world X coordinate of chunk origin"""
        return self.chunk_x * self.CHUNK_SIZE
    
    def get_world_z(self):
        """Get world Z coordinate of chunk origin"""
        return self.chunk_z * self.CHUNK_SIZE


class ChunkManager:
    """Manages chunks for infinite world generation"""
    
    CHUNK_RADIUS = 5  # Number of chunks to load around player
    
    def __init__(self, seed):
        self.seed = seed
        self.chunks = {}  # Dictionary mapping (chunk_x, chunk_z) to Chunk objects
        self.player_chunk_x = 0
        self.player_chunk_z = 0
        
    def update_player_position(self, world_x, world_z):
        """Update player position and load/unload chunks accordingly"""
        new_chunk_x = world_x // Chunk.CHUNK_SIZE
        new_chunk_z = world_z // Chunk.CHUNK_SIZE
        
        if new_chunk_x != self.player_chunk_x or new_chunk_z != self.player_chunk_z:
            self.player_chunk_x = new_chunk_x
            self.player_chunk_z = new_chunk_z
            self._load_chunks_around_player()
            self._unload_distant_chunks()
    
    def _load_chunks_around_player(self):
        """Load chunks around player"""
        for dx in range(-self.CHUNK_RADIUS, self.CHUNK_RADIUS + 1):
            for dz in range(-self.CHUNK_RADIUS, self.CHUNK_RADIUS + 1):
                chunk_x = self.player_chunk_x + dx
                chunk_z = self.player_chunk_z + dz
                chunk_key = (chunk_x, chunk_z)
                
                if chunk_key not in self.chunks:
                    self.chunks[chunk_key] = Chunk(chunk_x, chunk_z)
    
    def _unload_distant_chunks(self):
        """Unload chunks that are too far from player"""
        chunks_to_remove = []
        for chunk_key, chunk in self.chunks.items():
            dx = abs(chunk.chunk_x - self.player_chunk_x)
            dz = abs(chunk.chunk_z - self.player_chunk_z)
            
            if dx > self.CHUNK_RADIUS + 2 or dz > self.CHUNK_RADIUS + 2:
                chunks_to_remove.append(chunk_key)
        
        for chunk_key in chunks_to_remove:
            del self.chunks[chunk_key]
    
    def get_chunk(self, chunk_x, chunk_z):
        """Get chunk at given chunk coordinates"""
        chunk_key = (chunk_x, chunk_z)
        return self.chunks.get(chunk_key)
    
    def get_block(self, world_x, world_y, world_z):
        """Get block at world coordinates"""
        chunk_x = world_x // Chunk.CHUNK_SIZE
        chunk_z = world_z // Chunk.CHUNK_SIZE
        local_x = world_x % Chunk.CHUNK_SIZE
        local_z = world_z % Chunk.CHUNK_SIZE
        
        chunk = self.get_chunk(chunk_x, chunk_z)
        if chunk:
            return chunk.get_block(local_x, world_y, local_z)
        return 0
    
    def set_block(self, world_x, world_y, world_z, block_id):
        """Set block at world coordinates"""
        chunk_x = world_x // Chunk.CHUNK_SIZE
        chunk_z = world_z // Chunk.CHUNK_SIZE
        local_x = world_x % Chunk.CHUNK_SIZE
        local_z = world_z % Chunk.CHUNK_SIZE
        
        chunk = self.get_chunk(chunk_x, chunk_z)
        if chunk:
            chunk.set_block(local_x, world_y, local_z, block_id)
    
    def get_loaded_chunks(self):
        """Get all currently loaded chunks"""
        return list(self.chunks.values())