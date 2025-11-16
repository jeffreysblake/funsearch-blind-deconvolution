// Base types used across the application

export type UUID = string;
export type Timestamp = string; // ISO 8601 format

export interface BaseModel {
  id: UUID;
  created_at: Timestamp;
  updated_at: Timestamp;
}
