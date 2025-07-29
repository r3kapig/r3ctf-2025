const { Connection, Keypair, PublicKey, SystemProgram, Transaction, sendAndConfirmTransaction, ComputeBudgetProgram,
    LAMPORTS_PER_SOL
 } = require('@solana/web3.js');

async function interactWithContract() {
    const connection = new Connection('http://localhost:8899', 'confirmed');

    const payer = Keypair.generate();
    console.log(`New Account Address: ${payer.publicKey.toBase58()}`);

    const airdropSignature = await connection.requestAirdrop(
        payer.publicKey,
        1000 * LAMPORTS_PER_SOL
    );
    await connection.confirmTransaction(airdropSignature);
    console.log('Airdrop successful, account funded with 10 SOL');

    const computeLimitInstruction = ComputeBudgetProgram.setComputeUnitLimit({
        units: 1_400_000,
    });

    const computePriceInstruction = ComputeBudgetProgram.setComputeUnitPrice({
        microLamports: 1,
    });
    
    const programId = new PublicKey('CtMECpkMLovZFFFQMZJMoJyThYcJvy7wg17wRPHGbMRB');
    const programIdCallee = new PublicKey("5HbxJfBKytzL5bkgx5QhfkcAdUe7qEsxTsQdbe2tEWSC");

    const [pda, bump] = PublicKey.findProgramAddressSync(
        [Buffer.from("seed")],
        programId
    );

    const newAccount = Keypair.generate();
    
    const min_rent = await connection.getMinimumBalanceForRentExemption(0x100000);
    const createAccountIx = SystemProgram.createAccount({
        fromPubkey: payer.publicKey,
        newAccountPubkey: newAccount.publicKey,
        lamports: min_rent,
        space: 0x100000,
        programId: programId
    });

    const transaction = new Transaction()
    .add(createAccountIx);

    await sendAndConfirmTransaction(
        connection,
        transaction,
        [payer, newAccount]
    );

    const newAccount2 = Keypair.generate();
    const min_rent2 = await connection.getMinimumBalanceForRentExemption(0x10000);
    const createAccountIx2 = SystemProgram.createAccount({
        fromPubkey: payer.publicKey,
        newAccountPubkey: newAccount2.publicKey,
        lamports: min_rent2,
        space: 0x100,
        programId: programId,
    });

    const transaction2 = new Transaction()
    .add(createAccountIx2);

    await sendAndConfirmTransaction(
        connection,
        transaction2,
        [payer, newAccount2]
    );

    const newAccount3 = Keypair.generate();
    const min_rent3 = await connection.getMinimumBalanceForRentExemption(0x10000);
    const createAccountIx3 = SystemProgram.createAccount({
        fromPubkey: payer.publicKey,
        newAccountPubkey: newAccount3.publicKey,
        lamports: min_rent3,
        space: 0x100,
        programId: programId
    });
    const transaction3 = new Transaction()
    .add(createAccountIx3);

    await sendAndConfirmTransaction(
        connection,
        transaction3,
        [payer, newAccount3]
    );

    const instruction = {
        programId,
        keys: [
            { pubkey: newAccount.publicKey, isSigner: true, isWritable: true },
            { pubkey: newAccount2.publicKey, isSigner: true, isWritable: true },
            { pubkey: newAccount3.publicKey, isSigner: true, isWritable: true },
            { pubkey: pda, isSigner: false, isWritable: false },
            { pubkey: programIdCallee, isSigner: false, isWritable: true },
        ],
        data: Buffer.from([])
    };

    const transactionContract = new Transaction().add(computeLimitInstruction).add(computePriceInstruction).add(instruction);
    await sendAndConfirmTransaction(
        connection,
        transactionContract,
        [payer,newAccount,newAccount2,newAccount3]
    );
    const accountInfo = await connection.getAccountInfo(newAccount.publicKey);
    console.log('New Account Info Account1: ', accountInfo);

    const accountInfo2 = await connection.getAccountInfo(newAccount2.publicKey);
    console.log('New Account Info Account2: ', accountInfo2);

    const accountInfo3 = await connection.getAccountInfo(newAccount3.publicKey);
    console.log('New Account Info Account3: ', accountInfo3);
    
    return accountInfo2.data;
}

async function main() {
    while(true){
        data = await interactWithContract();
        const u64Value = data.readUInt32LE(0); 
        if(u64Value == 0x3e3e3e3e){
            console.log("Address not found. Continuing loop.");
        }else{
            break;
        }
    }
}

main();