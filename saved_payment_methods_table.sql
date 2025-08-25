-- Create saved_payment_methods table for storing user's tokenized payment methods
CREATE TABLE IF NOT EXISTS saved_payment_methods (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    payment_method_id VARCHAR(50) NOT NULL, -- MercadoPago payment method ID (visa, master, etc)
    last_four_digits VARCHAR(4) NOT NULL,
    card_holder_name VARCHAR(255) NOT NULL,
    expiration_month VARCHAR(2) NOT NULL,
    expiration_year VARCHAR(4) NOT NULL,
    issuer_name VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT fk_saved_payment_methods_user_id 
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
        
    -- Ensure unique combination of user and card (prevent duplicates)
    CONSTRAINT unique_user_card UNIQUE (user_id, last_four_digits, expiration_month, expiration_year)
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_saved_payment_methods_user_id ON saved_payment_methods(user_id);
CREATE INDEX IF NOT EXISTS idx_saved_payment_methods_active ON saved_payment_methods(is_active);

-- Add RLS (Row Level Security) policy
ALTER TABLE saved_payment_methods ENABLE ROW LEVEL SECURITY;

-- Policy: Users can only access their own saved payment methods
CREATE POLICY "Users can manage their own payment methods" ON saved_payment_methods
    USING (auth.uid() = user_id);