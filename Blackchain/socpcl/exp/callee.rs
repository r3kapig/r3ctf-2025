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
use std::{alloc::System, clone, rc::{self, Rc}};
use borsh::{BorshSerialize, BorshDeserialize};
use std::cell::{RefCell, Ref};

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
    instruction_data: &[u8],
) -> ProgramResult {
    let accounts_iter = &mut accounts.iter();
    let payer = next_account_info(accounts_iter)?;
    msg!("callee start");
    msg!("callee over");
    Ok(())
}