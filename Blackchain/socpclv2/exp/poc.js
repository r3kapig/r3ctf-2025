const { Connection, Keypair, PublicKey, SystemProgram, Transaction, sendAndConfirmTransaction, ComputeBudgetProgram,
    LAMPORTS_PER_SOL
 } = require('@solana/web3.js');

async function interactWithContract() {
    //   1. 连接到本地测试节点
    const connection = new Connection('http://localhost:8899', 'confirmed');

    // 2. 加载密钥对
    const payer = Keypair.generate();
    console.log(`新账户地址: ${payer.publicKey.toBase58()}`);

    const airdropSignature = await connection.requestAirdrop(
        payer.publicKey,
        1000 * LAMPORTS_PER_SOL
    );
    await connection.confirmTransaction(airdropSignature);
    console.log('空投成功, 账户已充值10 SOL');


    const computeLimitInstruction = ComputeBudgetProgram.setComputeUnitLimit({
        units: 1_400_000, // 请求 40 万 CU
    });

    const computePriceInstruction = ComputeBudgetProgram.setComputeUnitPrice({
        microLamports: 1, // 每个 CU 支付 1 微 Lamport
    });
    
    const programId = new PublicKey('2TefcqqrxgdD6eyVYyYtcxJJCeGhrYGGccxKH8S86GDU');
    const programIdCallee = new PublicKey("5oeqH9LtKU476pcWCUq21fL2M82Jasj6quo2iYb471fL");

    const [pda, bump] = PublicKey.findProgramAddressSync(
        [Buffer.from("seed")],
        programId
    );

    const newAccount = Keypair.generate();
    
    const min_rent = await connection.getMinimumBalanceForRentExemption(0x100000);
    // 创建账户指令
    

    const createAccountIx = SystemProgram.createAccount({ //receiver
        fromPubkey: payer.publicKey,
        newAccountPubkey: newAccount.publicKey,
        lamports: min_rent, // 初始金额（含租金）
        space: 0x100000,         // 账户存储空间
        // programId: programIdCallee, // 账户所属程序
        programId: programId // 账户所属程序
    });

    const transaction = new Transaction()
    .add(createAccountIx);

    await sendAndConfirmTransaction(
        connection,
        transaction,
        [payer, newAccount] // 新账户需要签名
    );

    // const accountInfo = await connection.getAccountInfo(newAccount.publicKey);
    // console.log('新账户信息Account1: ', accountInfo);

    const newAccount2 = Keypair.generate();
    const min_rent2 = await connection.getMinimumBalanceForRentExemption(0x10000);
    // 创建账户指令
    const createAccountIx2 = SystemProgram.createAccount({ //payer
        fromPubkey: payer.publicKey,
        newAccountPubkey: newAccount2.publicKey,
        lamports: min_rent2, // 初始金额（含租金）
        space: 0x100,         // 账户存储空间
        // programId: programIdCallee // 账户所属程序
        // programId
        programId: programId, // 账户所属程序
    });


    const transaction2 = new Transaction()
    .add(createAccountIx2);

    await sendAndConfirmTransaction(
        connection,
        transaction2,
        [payer, newAccount2] // 新账户需要签名
    );

    const newAccount3 = Keypair.generate();
    const min_rent3 = await connection.getMinimumBalanceForRentExemption(0x100000);
    const createAccountIx3 = SystemProgram.createAccount({ //receiver
        fromPubkey: payer.publicKey,
        newAccountPubkey: newAccount3.publicKey,
        lamports: min_rent3, // 初始金额（含租金）
        space: 0x100000,         // 账户存储空间
        // programId: programIdCallee, // 账户所属程序
        programId: programId // 账户所属程序
    });
    const transaction3 = new Transaction()
    .add(createAccountIx3);

    await sendAndConfirmTransaction(
        connection,
        transaction3,
        [payer, newAccount3] // 新账户需要签名
    );
    // const accountInfo2 = await connection.getAccountInfo(newAccount2.publicKey);
    // console.log('新账户信息Account2: ', accountInfo2);

    // 4. 调用合约
     // 5. 创建交易指令
    const instruction = {
        programId,
        keys: [
            // { pubkey: pda, isSigner: false, isWritable: false },
            { pubkey: newAccount3.publicKey, isSigner: true, isWritable: true }, // 新账户
            { pubkey: newAccount.publicKey, isSigner: true, isWritable: true }, // victim
            { pubkey: newAccount2.publicKey, isSigner: true, isWritable: true }, // 新账户
            // { pubkey: SystemProgram.programId, isSigner: false, isWritable: false },             // PDA账户
            { pubkey: programIdCallee, isSigner: false, isWritable: true },
            // { pubkey: programId, isSigner: false, isWritable: true }
        ],
        data: Buffer.from([]) // 根据实际指令结构编码
    };

    // 6. 创建并发送交易
    const transactionContract = new Transaction().add(computeLimitInstruction).add(computePriceInstruction).add(instruction);
    await sendAndConfirmTransaction(
        connection,
        transactionContract,
        [payer,newAccount3,newAccount,newAccount2]
    );
    const accountInfo = await connection.getAccountInfo(newAccount.publicKey);
    console.log('新账户信息Account1: ', accountInfo);

    const accountInfo2 = await connection.getAccountInfo(newAccount2.publicKey);
    console.log('新账户信息Account2: ', accountInfo2);

    // const accountInfo3 = await connection.getAccountInfo(newAccount3.publicKey);
    // console.log('新账户信息Account3: ', accountInfo3);
    return accountInfo.data;
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